# -*- coding: utf-8 -*-
import os
import logging
import json
from collections import OrderedDict  # @UnresolvedImport

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.fields.related import ForeignKey

from todoapp1.backend1.models import UserProfile, HandsontableDemo


class RecordErrors(Exception):
    pass


# Create your views here.

@staff_member_required
def handsontable_demo(request):
    """ defines/displays the HandsontableDemoTable's spreadsheet, and loads/saves the data. """
    MAX_ROWS = 100
    SPECIAL_PREFIX = '_hOt_'  # temporary ID prefix for new records, and prefix for special field values.
    context = RequestContext(request)
    search_term = request.GET.get('q') or ''
    context['search_term'] = search_term or ''
    table_cols = []
    #
    # very simple (and unnecessary) automatic column definitions
    # manually defining the "table_cols" array is usually better
    #
    for field in HandsontableDemo._meta.fields:
        coldef = {"data": field.name, "label": field.verbose_name, "type": "text",
                  "djangoBlank": field.blank or field.null, "djangoNull": field.null}
        table_cols.append(coldef)
        if isinstance(field, models.BooleanField):
            coldef['type'] = 'checkbox'
        elif isinstance(field, models.NullBooleanField):
            coldef['type'] = 'checkbox'
        elif isinstance(field, models.DateTimeField):
            coldef['type'] = 'datetime'
        elif isinstance(field, models.DateField):
            coldef['type'] = 'date'
        elif isinstance(field, models.TimeField):
            coldef['type'] = 'time'
        elif isinstance(field, models.ForeignKey):
            coldef['type'] = 'foreignkey'
            table_cols.pop()
        elif isinstance(field, models.IntegerField):
            coldef['type'] = 'numeric'
        elif isinstance(field, models.DecimalField):
            coldef['type'] = 'numeric'
        if field.choices:
            coldef['type'] = 'lookup'
            coldef['lookup_choices'] = OrderedDict(field.choices)
    table_cols_idx_by_name = {d['data']: d for d in table_cols}  # index, needed in the validation part
    # override some of the automatic definitions
    table_cols_idx_by_name['id']['readOnly'] = True
    table_cols_ids = [n['data'] for n in table_cols]

    def preprocess_field(value):
        pass

    if request.method == 'POST':
        if request.POST.get('changes'):
            errors = []
            changes = json.loads(request.POST['changes'])
            # NOTE: I'm not sure this is the right way to handle transactions in the new Django 1.6+ way...
            # but we *need* to catch and store errors on a per-record basis, to send back to the page.
            try:
                with transaction.atomic():
                    flag_error = False
                    for change in changes:
                        with transaction.atomic():
                            try:
                                pk = change.get('id', None)
                                assert pk is not None, 'a change without an ID field? %r' % change
                                # values to update
                                values = {k: preprocess_field(v) for k, v in change.items() if k != 'id' and not k.startswith(SPECIAL_PREFIX)}
                                logging.info('handsontable_demotable() change=%r', values)
                                if str(pk).startswith(SPECIAL_PREFIX + '_Id__'):
                                    rec = HandsontableDemo()
                                else:
                                    rec = HandsontableDemo.objects.get(pk=pk)
                                for k, v in values.items():
                                    setattr(rec, k, v)
                                rec.full_clean()
                                rec.save()
                            except ValidationError, e:
                                logging.error('handsontable_users() change=%r error=%r', change, e)
                                for fieldname, msg in e.message_dict.items():
                                    errors.append({'error': '%s: %s' % (fieldname, '; '.join(msg)), 'field': fieldname, 'item': change})
                                flag_error = True
                            except Exception, e:
                                logging.error('handsontable_users() change=%r error=%r', change, e)
                                errors.append({'error': unicode(e), 'item': change})
                                flag_error = True
                    if flag_error:
                        raise RecordErrors()
            except RecordErrors, e:
                pass  # it was expected, so no worriers
            if errors:
                return JsonResponse({'errors': errors})
        #
        # retrieve the data, applying filters and options
        #
        query = HandsontableDemo.objects.order_by('id')
        if search_term:
            query = query.filter(email__icontains=search_term)
        query = query[:MAX_ROWS]
        table_data = []
        for r in query:
            table_data.append({k: getattr(r, k) for k in table_cols_ids})
        logging.debug('handsontable... table response #recs=%s', len(table_data))
        return JsonResponse({'table_data': table_data})

    context['SPECIAL_PREFIX'] = SPECIAL_PREFIX
    context['MAX_ROWS'] = MAX_ROWS
    context['link_add'] = "#"
    context['link_list'] = reverse('handsontable_users')
    context['table_columns'] = json.dumps(table_cols)

    return render_to_response("handsontable_users.html", context)


# Create your views here.

@staff_member_required
def handsontable_users(request):
    """ defines/displays the User's handsontable grid, and also loads and saves the data """
    context = RequestContext(request)
    search_term = request.GET.get('q') or ''
    context['search_term'] = search_term or ''
    MAX_ROWS = 100

    table_cols = [
                  {"data": "id", "label": "id", "type": "text", "readOnly": True},
                  {"data": "email", "label": "email", "type": "text"},
                  {"data": "first_name", "label": "first_name", "type": "text"},
                  {"data": "last_name", "label": "last_name", "type": "text"},
                  {"data": "last_login", "label": "last_login", "type": "datetime"},
                  {"data": "is_active", "label": "last_login", "type": "checkbox"},
                  ]
    table_cols_ids = [n['data'] for n in table_cols]
    if request.method == 'POST':
        last_error = None
        if request.POST.get('changes'):
            changes = json.loads(request.POST['changes'])
            change = None
            try:
                with transaction.atomic():
                    for change in changes:
                        logging.info('handsontable_users() change=%r', change)
                        assert change.get('id'), 'a change without an ID? %r' % change
                        # NOTE: datetime/date/time fields must be MANUALLY deserialized
                        # NOTE: validation goes here.
                        pk = change.pop('id')
                        if str(pk).startswith('_Temporary_ID_'):
                            if not change.get('email'):
                                raise ValidationError('email is required')
                            UserProfile.objects.create(**change)
                        else:
                            # validation: while updating, the values can be unset... so we have to check for SET and empty string... that's why the 'dummy' value
                            if not change.get('email', 'dummy'):
                                raise ValidationError('email is required')
                            UserProfile.objects.filter(pk=pk).update(**change)
            except Exception, e:
                logging.error('handsontable_users() change=%r error=%r', change, e)
                last_error = e
        if last_error:
            return JsonResponse({'errors': [str(last_error)]})
        #
        # retrieve the data, applying filters and options
        #
        query = UserProfile.objects.order_by('first_name', 'last_name')
        if search_term:
            query = query.filter(email__icontains=search_term)
        query = query[:MAX_ROWS]
        table_data = []
        for r in query:
            table_data.append({k: getattr(r, k) for k in table_cols_ids})
        return JsonResponse({'table_data': table_data})

    context['MAX_ROWS'] = MAX_ROWS
    context['link_add'] = "#"
    context['link_list'] = reverse('handsontable_users')
    context['table_columns'] = json.dumps(table_cols)

    return render_to_response("handsontable_users.html", context)
