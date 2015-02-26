# -*- coding: utf-8 -*-
import logging
import time
import uuid

from django.db import models
from django.db import transaction
from django.db.utils import IntegrityError
from django.contrib.auth.models import User as DjangoUser
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from django.core.exceptions import ObjectDoesNotExist

from api_utils import ApiException
from error_messages import ERRORS

from django.db.backends.signals import connection_created
from django.dispatch import receiver


@receiver(connection_created)
def extend_sqlite(connection=None, **kwargs):
    if connection.vendor == "sqlite":
        def pg_concat(*args):
            return ''.join(args)
        connection.connection.create_function("concat", -1, pg_concat)

# monkey-patching django to allow for usernames > 30 chars. The SQL table must be changed MANUALLY
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator
username = User._meta.get_field("username")
username.max_length = 254
for v in username.validators:
    if isinstance(v, MaxLengthValidator):
        v.limit_value = 254


def _unique_rname():
    return u'#%s' % uuid.uuid4().hex


class BaseModel(models.Model):
    class Meta:
        abstract = True
    rname = models.CharField(max_length=255, null=False, blank=True, unique=True,
                             default=_unique_rname,
                             help_text='Internal object name (fit for admin/backend tasks, must be unique)')
    date_created = CreationDateTimeField()
    date_updated = ModificationDateTimeField()

    def __unicode__(self):
        return self.rname or '(no rname)'

    @classmethod
    def upsert(cls, conds=None, **kwargs):
        assert conds
        try:
            rec = cls.objects.get(**conds)
        except ObjectDoesNotExist:
            rec = cls()
        for k, v in kwargs.items():
            setattr(rec, k, v)
        rec.save()
        return rec

    def save(self, *args, **kwargs):
        try:
            super(BaseModel, self).save(*args, **kwargs)
        except IntegrityError:
            # if there is an integrity error, chances are it's because rname. Retry
            self.rname += ' #' + _unique_rname()
            super(BaseModel, self).save(*args, **kwargs)


class UserProfile(DjangoUser):
    """ Since Django User inheritance is not the best way to go (and uneeded in this case), simply create a proxy """
    class Meta:
        proxy = True

    @property
    def rname(self):
        return '%s %s %s' % (self.first_name, self.last_name, self.email)

    def serialize(self):
        """ expose object via the API """
        return {
                'email': self.email,
                }

    def serialize_curr_user(self):
        """ expose object via the API """
        return {
             'email': self.email,
             'first_name': self.first_name,
             'last_name': self.last_name,
             }

    @classmethod
    def create_user(cls, email=None, password=None, first_name=None, last_name=None):
        try:
            curr_user = UserProfile.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
              )
            curr_user.full_clean()
            curr_user.save()
        except IntegrityError:
            raise ApiException(*ERRORS.signup_email_already_exists)
        return curr_user


class TODOList(BaseModel):
    title = models.CharField(max_length=255, null=False, blank=False)
    comments = models.TextField(null=False, blank=True)
    category = models.CharField(max_length=255, null=False, blank=True)
    created_by = models.ForeignKey(UserProfile, null=True)
    status = models.IntegerField(null=False, default=0, choices=(
                                                      (0, 'active'),
                                                      (1, 'archived'),
                                                      ))

    @classmethod
    def upsert(cls, title=None, comments=None, category=None, status=None, curr_user=None, todolist=None):
        assert curr_user and title
        # in case we're updating, check it's either my list or it's shared with me
        if todolist:
            if todolist.created_by != curr_user:
                raise ApiException(*ERRORS.cannot_access_list)

        with transaction.atomic():
            todolist = todolist or TODOList()
            todolist.title = title
            todolist.comments = comments or ''
            todolist.category = category or ''
            todolist.created_by = todolist.created_by or curr_user
            todolist.status = status or 0
            todolist.save()
        return todolist

    def share_with(self, curr_user=None, shared_with=None):
        assert curr_user and shared_with
        # check it's either my list or it's shared with me
        if self.created_by != curr_user:
            if TODOListSharing.objects.filter(todolist=self, shared_with=curr_user).count() == 0:
                raise ApiException(*ERRORS.cannot_access_list)
        if curr_user == shared_with:
            raise ApiException(*ERRORS.cannot_access_list)

        with transaction.atomic():
            rec = TODOListSharing()
            rec.todolist = self
            rec.shared_by = curr_user
            rec.shared_with = shared_with
            rec.save()
        return rec

    @classmethod
    def list(cls, search=None, category=None, curr_user=None, todolist_id=None):
        """ return a specific TO-DO list or all the lists visible to curr_user that matches the search """
        assert curr_user
        results = []
        # are we retrieving a specific list?
        if todolist_id:
            todolist = TODOList.objects.get(pk=todolist_id)
            if todolist.created_by != curr_user:
                for t in TODOListSharing.objects.filter(todolist=todolist, shared_with=curr_user):
                    todolist = t.todolist
                    break
                else:
                    raise ApiException(*ERRORS.cannot_access_list)
            results = [todolist]
        if not results:
            query = TODOList.objects.filter(created_by=curr_user)
            if search:
                query = query.filter(title__istartswith=search)
            if category:
                query = query.filter(category=category)
            for t in query.order_by('title'):
                results.append(t)
            query = TODOListSharing.objects.filter(shared_with=curr_user)
            if search:
                query = query.filter(todolist__title__istartswith=search)
            if category:
                query = query.filter(todolist__category=category)
            for t in query.order_by('todolist__title'):
                results.append(t.todolist)
        return results

    def save(self, *args, **kwargs):
        self.rname = '%s, by %s %s' % (self.title, self.created_by.email, _unique_rname())
        super(TODOList, self).save(*args, **kwargs)

    def serialize(self):
        """ expose object via the API """
        return {
                'id': self.id,
                'title': self.title,
                'comments': self.comments,
                'category': self.category,
                'status': self.status,
                'created_by': self.created_by.serialize(),
                'count_items': self.todolistitems.count(),
                'items': [x.serialize() for x in self.todolistitems.all()],
                }


class TODOListItem(BaseModel):
    todolist = models.ForeignKey(TODOList, related_name='todolistitems')
    text = models.CharField(max_length=255, null=False, blank=False)
    status = models.IntegerField(null=False, default=0, choices=(
                                                      (0, 'not started'),
                                                      (1, 'started'),
                                                      (2, 'completed'),
                                                      ))
    created_by = models.ForeignKey(UserProfile, related_name='+')
    last_updated_by = models.ForeignKey(UserProfile, null=True, related_name='+')

    @classmethod
    def upsert(cls, text=None, status=None, curr_user=None, todolist=None, todolistitem=None):
        assert text and curr_user
        # check it's either my list or it's shared with me
        if todolistitem:
            if todolistitem.todolist.created_by != curr_user:
                if TODOListSharing.objects.filter(todolist=todolistitem.todolist, shared_with=curr_user).count() == 0:
                    raise ApiException(*ERRORS.cannot_access_list)
        else:
            assert todolist
        with transaction.atomic():
            todolistitem = todolistitem or TODOListItem()
            todolistitem.todolist = todolist
            todolistitem.text = text
            todolistitem.status = status or 0
            todolistitem.created_by = todolistitem.created_by_id and todolistitem.created_by or curr_user
            todolistitem.last_updated_by = curr_user
            todolistitem.save()
        return todolistitem

    def serialize(self):
        """ expose object via the API """
        return {
                'id': self.id,
                'text': self.text,
                'status': self.status,
                'last_updated_by': self.last_updated_by.serialize(),
                }


class TODOListSharing(BaseModel):
    class Meta:
        unique_together = (("todolist", "shared_with"),)
    todolist = models.ForeignKey(TODOList)
    shared_by = models.ForeignKey(UserProfile, related_name='shared_with')
    shared_with = models.ForeignKey(UserProfile, related_name='shared_by')


class HandsontableDemo(BaseModel):
    test_foreign_key_null = models.ForeignKey(UserProfile, null=True, blank=True, related_name='+')
    test_foreign_key = models.ForeignKey(UserProfile, related_name='+')
    test_charfield = models.CharField(max_length=255, null=False, blank=False)
    test_int_choices_null = models.IntegerField(null=True, blank=True, choices=(
                                                      (0, 'zero'),
                                                      (1, 'one'),
                                                      (2, 'two'),
                                                      ))
    test_int_choices = models.IntegerField(null=False, default=0, choices=(
                                                      (0, 'zero'),
                                                      (1, 'one'),
                                                      (2, 'two'),
                                                      ))
    test_integer = models.IntegerField(null=False)
    test_integer_null = models.IntegerField(null=True, blank=True)

    test_decimal = models.DecimalField(max_digits=7, decimal_places=2, null=False)
    test_decimal_null = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)

    test_boolean = models.BooleanField(null=False, default=False)
    test_boolean_null = models.NullBooleanField(null=True, blank=True)

    test_datetime_null = models.DateTimeField(null=True, blank=True)
    test_date = models.DateField(null=True, blank=True)
    test_time = models.TimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.rname = '%s %s %s' % (self.test_charfield, self.test_foreign_key, _unique_rname())
        super(HandsontableDemo, self).save(*args, **kwargs)
