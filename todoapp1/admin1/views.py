# -*- coding: utf-8 -*-
import os
import logging
import json
from collections import OrderedDict  # @UnresolvedImport
import pprint

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.fields.related import ForeignKey

from todoapp1.backend1.models import UserProfile, HandsontableDemo


@staff_member_required
def generic_userprofile_autocomplete(request):
    MAX_ROWS = 20
    search_term = request.GET.get('query') or ''
    query = UserProfile.objects.order_by('first_name', 'last_name')
    if search_term:
        query = query.filter(email__icontains=search_term)
    query = query[:MAX_ROWS]
    items = [{'id': e.id, 'text': '%s %s %s' % (e.first_name, e.last_name, e.email)} for e in query]
    return JsonResponse({'items': items}, safe=False)


HANDSONTABLE_FIELD_PREFIX = '_hOt_'  # temporary ID prefix for new records, and prefix for special field values.
HANDSONTABLE_MAX_ROWS = 100


class RecordErrors(Exception):
    pass


def handsontable_process_rows(row, changes, table_cols_idx_by_name):
    """  pre-process each row according to the column definition """
    pass


def handsontable_process_change(change, table_cols_ids):
    """  validates and process the the changes to be made the record """

    pk = change.get('id', None)
    assert pk is not None, 'a change without an ID field? %r' % change
    if str(pk).startswith(HANDSONTABLE_FIELD_PREFIX + '_Id__'):
        pk = None  # new record
    if change.get(HANDSONTABLE_FIELD_PREFIX + '_flag_delete_record__'):
        assert pk is not None, 'a delete without an ID field? %r' % change
        return pk, True, None
    values = {k: v for k, v in change.items() if k != 'id' and not k.startswith(HANDSONTABLE_FIELD_PREFIX)}
    for coldef in table_cols_ids:
        name = coldef['data']
        if coldef['type'] == 'foreignkey':
            name_label = name + '__L'
            if name_label in values:
                assert name in values, 'missing field: %s %r' % (name, values)
                values[name + '_id'] = values.pop(name)  # replace fieldname=pk with fieldname_id=pk
                values.pop(name_label)  # discard the label part
        elif coldef['type'] == 'lookup':
            name_label = name + '__L'
            if name in values:
                assert name in values, 'missing field: %s_id %r' % (name, values)
                values.pop(name_label)  # discard the label part
        elif coldef['type'] == 'datetime':
            pass
        elif coldef['type'] == 'date':
            pass
        elif coldef['type'] == 'time':
            pass
    return pk, False, values


def handsontable_demo_save(changes, table_cols_ids):
    errors = []
    # NOTE: I'm not sure this is the right way to handle transactions in the new Django 1.6+ way...
    # but we *need* to catch and store errors on a per-record basis, to send back to the page.
    try:
        with transaction.atomic():
            flag_error = False
            for change in changes:
                with transaction.atomic():
                    try:
                        pk, delete, values = handsontable_process_change(change, table_cols_ids)
                        if not pk:
                            rec = HandsontableDemo()
                        else:
                            rec = HandsontableDemo.objects.get(pk=pk)
                            if delete:
                                rec.delete()
                                continue
                        for k, v in values.items():
                            setattr(rec, k, v)
                        rec.full_clean()
                        rec.save()
                    except ValidationError, e:
                        logging.error('handsontable_users() change=%r validation=%r', change, e)
                        temp = getattr(e, 'error_dict', {})
                        if temp:
                            for fn, fe in temp.items():
                                errors.append({'error': repr(fe), 'field': fn, 'item': change})
                        else:
                            for fe in e.messages:
                                errors.append({'error': repr(fe), 'item': change})
                        flag_error = True
                    except Exception, e:
                        # unexpected (non-validation) error...
                        logging.error('handsontable_users() change=%r error=%r', change, e)
                        errors.append({'error': repr(e), 'item': change})
                        flag_error = True
            if flag_error:
                raise RecordErrors()
    except RecordErrors, e:
        pass  # it was expected, so no worriers
    return errors


@staff_member_required
def handsontable_demo(request):
    """ defines/displays the HandsontableDemoTable's spreadsheet, and loads/saves the data. """
    context = RequestContext(request)
    search_term = request.GET.get('q') or ''
    context['search_term'] = search_term or ''
    table_cols = []

    #
    # very simple (and unnecessary) automatic column definitions
    # manually defining the "table_cols" array is usually better
    #
    for field in HandsontableDemo._meta.fields:
        coldef = {"data": field.name,
                  "label": field.verbose_name,
                  "type": "text",
                  "djangoBlank": field.blank or field.null,
                  "djangoNull": field.null
                  }
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
            table_cols.append({'data': coldef['data'] + '_id', 'type': 'hidden'})
            coldef['type'] = 'foreignkey'
            coldef['fieldname'] = coldef['data']
            coldef['data'] += '__L'
            coldef['lookup_remote_url'] = reverse('admin:backend1_handsontabledemo_autocomplete', args=[coldef['fieldname']])
        elif isinstance(field, models.IntegerField):
            coldef['type'] = 'numeric'
        elif isinstance(field, models.DecimalField):
            coldef['type'] = 'numeric'
        if field.choices:
            table_cols.append({'data': coldef['data'], 'type': 'hidden'})
            coldef['type'] = 'lookup'
            coldef['fieldname'] = coldef['data']
            coldef['data'] += '__L'
            coldef['lookup_choices'] = OrderedDict(field.choices)
    table_cols_idx_by_name = {d['data']: d for d in table_cols}  # index, needed in the validation part
    # override some of the automatic definitions
    table_cols_idx_by_name['id']['readOnly'] = True
    table_cols_idx_by_name['id']['renderer'] = 'detaillink_Renderer'  # special renderer to display a link to the detail page
    table_cols_idx_by_name['id']['detail_url'] = reverse('admin:backend1_handsontabledemo_change', args=['(id)'])
    table_cols_idx_by_name['rname']['readOnly'] = True
    table_cols_ids = [n['data'] for n in table_cols]

    #
    # save and/or retrieve the data, applying filters and options
    #
    if request.method == 'POST':
        if request.POST.get('changes'):
            errors = handsontable_demo_save(json.loads(request.POST['changes']),
                                            table_cols_ids,
                                            table_cols_idx_by_name)
            if errors:
                return JsonResponse({'errors': errors})
        query = HandsontableDemo.objects.order_by('id')
        if search_term:
            query = query.filter(email__icontains=search_term)
        query = query[:HANDSONTABLE_MAX_ROWS]
        table_data = []
        for r in query:
            rec = {k: getattr(r, k, None) for k in table_cols_ids if not k.endswith('__L')}
            # pre-process each field choices, or foreign-keys
            rec['test_int_choices__L'] = table_cols_idx_by_name['test_int_choices__L']['lookup_choices'].get(r.test_int_choices)
            rec['test_int_choices_null__L'] = table_cols_idx_by_name['test_int_choices_null__L']['lookup_choices'].get(r.test_int_choices_null)
            if r.test_foreign_key_id is not None:
                rec['test_foreign_key__L'] = r.test_foreign_key.rname
            if r.test_foreign_key_null_id is not None:
                rec['test_foreign_key_null__L'] = r.test_foreign_key_null.rname
            table_data.append(rec)
        logging.debug('handsontable... table response #recs=%s', len(table_data))
        return HttpResponse(json.dumps({'table_data': table_data}, cls=DjangoJSONEncoder), content_type='application/json')

    context['SPECIAL_PREFIX'] = HANDSONTABLE_FIELD_PREFIX
    context['MAX_ROWS'] = HANDSONTABLE_MAX_ROWS
    context['link_list'] = reverse('handsontable_users')
    context['table_columns'] = json.dumps([x for x in table_cols if x['type'] != 'hidden'])

    return render_to_response("handsontable_demo.html", context)


# Create your views here.

@staff_member_required
def handsontable_users(request):
    """ defines/displays the User's handsontable grid, and also loads and saves the data """
    context = RequestContext(request)
    search_term = request.GET.get('q') or ''
    context['search_term'] = search_term or ''

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
        query = query[:HANDSONTABLE_MAX_ROWS]
        table_data = []
        for r in query:
            table_data.append({k: getattr(r, k) for k in table_cols_ids})
        return JsonResponse({'table_data': table_data})

    context['MAX_ROWS'] = HANDSONTABLE_MAX_ROWS
    context['link_add'] = "#"
    context['link_list'] = reverse('handsontable_users')
    context['table_columns'] = json.dumps(table_cols)

    return render_to_response("handsontable_user.html", context)
