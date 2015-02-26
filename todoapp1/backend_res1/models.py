# -*- coding: utf-8 -*-
import logging
import datetime
import random
import time
from django.conf import settings

from django.db import models, connection
from django.db import transaction
from django.db.utils import IntegrityError
from django.contrib.auth.models import User as DjangoUser
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from django.core.exceptions import ObjectDoesNotExist

"""
- rname is useful for several admin tools: foreign key lookup, searches, logging, auditing.

- "is_active" is vital for two reasons: deleting a record is not an option most of the time, and creating and object does not mean one wants to actually use it ( you need to create a city for restaurants, but you do not want to show that city or its restaurants until next week).

- date_created and date_updated are useful fields for periodic processes and auditing.

- "t8id" is the link to the table8 DB.

- Customer.user is OPTIONAL (not all Customers are registered as users).

"""


def _unique_rname():
    return u'#%s%s' % (time.time(), random.randint(0, 999))


class BaseModel(models.Model):
    class Meta:
        abstract = True
    rname = models.CharField(max_length=255, null=True, unique=True,
                             default=_unique_rname,
                             help_text='unique, human-readable record name')
    date_created = CreationDateTimeField()
    date_updated = ModificationDateTimeField()

    def __unicode__(self):
        return self.rname or '(no rname)'

    @classmethod
    def upsert(cls, conds=None, **kwargs):
        """ create/update a record. """
        assert conds
        try:
            rec = cls.objects.get(**conds)
        except ObjectDoesNotExist, e:
            rec = cls()
        for k, v in kwargs.items():
            setattr(rec, k, v)
        rec.full_clean()
        rec.save()
        return rec

    @classmethod
    def upsert_if_changed(cls, conds=None, **kwargs):
        """ create/update a record. Only saves if changes were made! """
        assert conds
        try:
            rec = cls.objects.get(**conds)
        except ObjectDoesNotExist, e:
            rec = cls()
        has_changes = False
        for k, v in kwargs.items():
            orig_value = getattr(rec, k, [None])
            if orig_value != v:
                setattr(rec, k, v)
                has_changes = True
        rec.full_clean()
        if has_changes:
            rec.save()
        return rec

    def save(self, *args, **kwargs):
        with transaction.atomic():
            try:
                with transaction.atomic():
                    super(BaseModel, self).save(*args, **kwargs)
            except IntegrityError:
                # if there is an integrity error, chances are it's because rname. Retry
                self.rname += ' #' + _unique_rname()
                super(BaseModel, self).save(*args, **kwargs)


class Region(BaseModel):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True, help_text='If unchecked, it will not be used in the website')
    latitude = models.DecimalField(max_digits=10, decimal_places=5, default=0)
    longitude = models.DecimalField(max_digits=10, decimal_places=5, default=0)
    t8id = models.CharField(max_length=32, null=True, blank=True, db_index=True)

    def save(self, *args, **kwargs):
        self.rname = self.name
        super(Region, self).save()


class Restaurant(BaseModel):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True, help_text='If unchecked, it will not be used in the website')

    short_description = models.CharField(max_length=255, blank=True)
    region = models.ForeignKey(Region)
    latitude = models.DecimalField(max_digits=10, decimal_places=5, default=0)
    longitude = models.DecimalField(max_digits=10, decimal_places=5, default=0)
    address = models.CharField(max_length=255, blank=True)

    cuisine = models.CharField(max_length=255, blank=True)
    ambiance = models.CharField(max_length=255, blank=True)
    noise = models.CharField(max_length=255, blank=True)
    attire = models.CharField(max_length=255, blank=True)
    private_rooms = models.CharField(max_length=255, blank=True)
    private_rooms_max_no = models.CharField(max_length=255, blank=True)

    price = models.CharField(max_length=255, blank=True)
    tasting_only = models.CharField(max_length=255, blank=True)
    lunch_dinner = models.CharField(max_length=255, blank=True)
    hard_alcohol = models.CharField(max_length=255, blank=True)
    pre_dinner = models.CharField(max_length=255, blank=True)
    no_amex = models.CharField(max_length=255, blank=True)
    sold_out = models.CharField(max_length=255, blank=True)

    opentable_id = models.CharField(max_length=255, blank=True)
    rezbook = models.CharField(max_length=255, blank=True)
    seat_me_url = models.CharField(max_length=255, blank=True)
    other = models.CharField(max_length=255, blank=True)
    t8id = models.CharField(max_length=32, null=True, blank=True, db_index=True)

    def save(self, *args, **kwargs):
        self.rname = '%.50s, %.50s' % (self.name, self.region.name)
        super(Restaurant, self).save()


class Hotel(BaseModel):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True, help_text='If unchecked, it will not be used in the website')
    user = models.ForeignKey(DjangoUser, null=True)
    region = models.ForeignKey(Region)
    t8id = models.CharField(max_length=32, null=True, blank=True, db_index=True)

    def save(self, *args, **kwargs):
        self.rname = u'%s, %s' % (self.name, self.email or _unique_rname())
        super(Hotel, self).save()


class Concierge(BaseModel):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True, help_text='If unchecked, it will not be used in the website')
    user = models.ForeignKey(DjangoUser, null=True, blank=True)
    hotel = models.ForeignKey(Hotel, null=True, blank=True)
    t8id = models.CharField(max_length=32, null=True, blank=True, db_index=True)

    def save(self, *args, **kwargs):
        self.rname = u'%s, %s' % (self.name, self.email or _unique_rname())
        with transaction.atomic():
            super(Concierge, self).save()
            if self.user_id:
                self.user.email = self.email
                self.user.save()


class Customer(BaseModel):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True, help_text='If unchecked, it will not be used in the website')
    user = models.ForeignKey(DjangoUser, null=True, blank=True)
    t8id = models.CharField(max_length=32, null=True, blank=True, db_index=True)

    def save(self, *args, **kwargs):
        self.rname = '%s, %s' % (self.name, self.email or _unique_rname())
        with transaction.atomic():
            super(Customer, self).save()
            if self.user_id:
                self.user.email = self.email
                self.user.save()


class Staff(BaseModel):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True, help_text='If unchecked, it will not be used in the website')
    user = models.ForeignKey(DjangoUser, null=True, blank=True)
    t8id = models.CharField(max_length=32, null=True, blank=True, db_index=True)

    def save(self, *args, **kwargs):
        self.rname = '%s, %s' % (self.name, self.email or _unique_rname())
        with transaction.atomic():
            super(Staff, self).save()
            if self.user_id:
                self.user.email = self.email
                self.user.save()


def _generate_reservation_time_range():
    tstart = datetime.datetime(2000, 1, 1, 11, 0)
    tstep = datetime.timedelta(minutes=15)
    yield tstart.time(), tstart.strftime("%I%p")
    for dummy in range(1, 60):
        tstart += tstep
        yield tstart.time(), tstart.strftime("%I:%M%p").strip('0').lower()


class Reservation(BaseModel):
    SEATS_CHOICE = ((2, '2_seats'), (4, '4_seats'), (6, '6_seats'),)
    TIME_CHOICE = list(_generate_reservation_time_range())

    order_no = models.IntegerField()
    restaurant = models.ForeignKey(Restaurant)
    res_date = models.DateField(verbose_name='Date')
    res_time = models.TimeField(verbose_name='Time', default=TIME_CHOICE[0][0], choices=TIME_CHOICE)  # time-slot reserved.
    res_partysize = models.IntegerField(choices=SEATS_CHOICE, default=SEATS_CHOICE[0][0], verbose_name='seats')
    amount_paid = models.DecimalField(verbose_name='Amount paid', max_digits=8, decimal_places=2, default=50.0)
    purchase_date = models.DateTimeField(verbose_name='Purchased Date')
    customer = models.ForeignKey(Customer)
    concierge = models.ForeignKey(Concierge, null=True, blank=True)

    is_active = models.BooleanField(default=True, help_text='If unchecked, it will not be used in the website')
    t8id = models.CharField(max_length=32, null=True, blank=True, db_index=True)

    def save(self, *args, **kwargs):
        self.rname = '%.50s %.10s %.10s %.50s #%s' % (self.restaurant.name, self.res_date, self.res_time, self.order_no, self.customer.name)
        super(Reservation, self).save()
