# -*- coding: utf-8 -*-
import os
import logging
import json
import datetime
import pprint
from collections import OrderedDict  # @UnresolvedImport


from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from django.db import models
from django.db.models.loading import get_model

from todoapp1.backend1.utils import dt_server_now, dt_server_to_local, dt_local_to_server, dt_string_to_server


HANDSONTABLE_FIELD_PREFIX = '_hOt_'  # temporary ID prefix for new records, and prefix for special field values.
HANDSONTABLE_MAX_ROWS = 100


class RecordErrors(Exception):
    pass


def handsontable_process_rows(rec, table_cols, table_cols_idx_by_name):
    """  pre-process each row according to the column definition """

    row = {k['data']: getattr(rec, k['data'], None) for k in table_cols if not k['data'].endswith('__L')}
    for coldef in table_cols:
        if coldef['type'] == 'foreignkey':
            name = coldef['fieldname'].replace('_id', '')  # remove the foreinkey"_id" part
            if getattr(rec, name) is not None:
                row[coldef['data']] = unicode(getattr(rec, name))
        elif coldef['type'] == 'lookup':
            name = coldef['fieldname']
            row[coldef['data']] = coldef['lookup_choices'].get(getattr(rec, name))
    return row


def handsontable_process_change(change, table_cols):
    """  validates and process the the changes to be made the record """

    pk = change.pop('id', None)
    assert pk is not None, 'a change without an ID field? %r' % change
    if str(pk).startswith(HANDSONTABLE_FIELD_PREFIX + '_Id__'):
        pk = None  # new record
    if change.get(HANDSONTABLE_FIELD_PREFIX + '_flag_delete_record__'):
        assert pk is not None, 'a delete without an ID field? %r' % change
        return pk, True, None
    values = {k: v for k, v in change.items() if not k.startswith(HANDSONTABLE_FIELD_PREFIX)}
    logging.debug('handsontable_process_change values=%r', values)
    for coldef in table_cols:
        name = coldef.get('fieldname') or coldef['data']
        if name in values:
            if coldef['type'] == 'foreignkey':
                name_label = coldef['data']
                if name_label in values:
                    assert name in values, 'missing field: %s %r' % (name, values)
                    values[name] = values.pop(name)  # replace fieldname=pk with fieldname_id=pk
                    values.pop(name_label)  # discard the label part
            elif coldef['type'] == 'lookup':
                name_label = coldef['data']
                if name in values:
                    assert name in values, 'missing field: %s_id %r' % (name, values)
                    values.pop(name_label)  # discard the label part
            elif coldef['type'] == 'datetime':
                # DISPLAY_TIME_ZONE
                if name in values:
                    values[name] = values[name] and dt_string_to_server(datetime.datetime.strptime(values[name], "%Y-%m-%d %H:%M")) or None
            elif coldef['type'] == 'date':
                if name in values:
                    values[name] = values[name] and dt_string_to_server(datetime.datetime.strptime(values[name], "%Y-%m-%d")) or None
            elif coldef['type'] == 'time':
                if name in values:
                    values[name] = values[name] and dt_string_to_server(datetime.datetime.strptime(values[name], "%H:%M:%S")) or None
    logging.debug('handsontable_process_change after=%r', values)
    return pk, False, values


def handsontable_generic_save(changes, table_cols_ids, modelClass):
    """ create/update/delete of each change in "changes". Most of the code is devoted to error handling. """

    errors = []
    # NOTE: I'm not sure this is the right way to handle transactions in the new Django 1.6+ way...
    # it says never catch an exception inside atomic()
    # but we *need* to catch and store errors on a per-record basis, to send back to the page.
    try:
        with transaction.atomic():
            flag_error = False
            for change in changes:
                pk = None
                with transaction.atomic():
                    try:
                        pk, delete, values = handsontable_process_change(change, table_cols_ids)
                        if not pk:
                            rec = modelClass()
                        else:
                            rec = modelClass.objects.get(pk=pk)
                            if delete:
                                rec.delete()
                                continue
                        for k, v in values.items():
                            setattr(rec, k, v)
                        rec.full_clean()
                        rec.save()
                    except ValidationError, e:
                        logging.error('handsontable_XXX_save() pk=%s change=%r validation=%r', pk, change, e)
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
                        logging.error('handsontable_XXX_save() pk=%s change=%r error=%r', pk, change, e)
                        errors.append({'error': repr(e), 'item': change})
                        flag_error = True
                        raise
            if flag_error:
                raise RecordErrors()
    except RecordErrors, e:
        pass
    return errors


@staff_member_required
def handsontable_generic_view(request, app_name=None, model_name=None):
    """ defines/displays any model spreadsheet. Not really useful, you should always create a custom view per model """

    MODEL = get_model(app_name, model_name)

    #
    # very simple automatic column definition
    #
    table_cols = []
    for field in MODEL._meta.fields:
        # skip certain fields
        if field.name in ('date_created', 'date_updated', 'rname'):
            continue
        coldef = {"data": field.name,
                  "label": field.verbose_name,
                  "type": "text",
                  "djangoBlank": field.blank or field.null,
                  "djangoNull": field.null
                  }
        table_cols.append(coldef)
        if isinstance(field, models.BooleanField):
            coldef['type'] = 'checkbox'
            # coldef['renderer'] = 'checkbox1'
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
            coldef['fieldname'] = coldef['data'] + '_id'
            coldef['data'] += '__L'
            try:
                coldef['link_to'] = reverse('spreadsheet_%s' % (field.rel.to._meta.model_name)) + '?id__exact=%28val%29'
            except NoReverseMatch, e:
                logging.error(e)
                try:
                    coldef['link_to'] = reverse('admin:%s_%s_change' % (app_name, field.rel.to._meta.model_name), args=['(val)'])
                except NoReverseMatch, e:
                    logging.error(e)
            coldef['lookup_remote_url'] = reverse('generic_autocomplete', kwargs={
                                                                                  'app_name': app_name,
                                                                                  'model_name': field.rel.to._meta.model_name,
                                                                                  'field_name': coldef['fieldname']})
        elif isinstance(field, models.IntegerField):
            coldef['type'] = 'numeric'
        elif isinstance(field, models.DecimalField):
            coldef['format'] = '0,0.00'
            coldef['type'] = 'numeric'
        if field.choices:
            table_cols.append({'data': coldef['data'], 'type': 'hidden'})
            coldef['type'] = 'lookup'
            coldef['fieldname'] = coldef['data']
            coldef['data'] += '__L'
            coldef['lookup_choices'] = OrderedDict([(unicode(k), v) for k, v in field.choices])
    # prepare some indexes for fast access to column defs
    table_cols_idx_by_name = {d['data']: d for d in table_cols}

    # override some of the automatic definitions
    table_cols_idx_by_name['id']['readOnly'] = True
    table_cols_idx_by_name['id']['renderer'] = 'detaillink_Renderer'
    table_cols_idx_by_name['id']['link_to'] = reverse('admin:%s_%s_change' % (app_name, model_name), args=['(val)'])
    # table_cols_idx_by_name['rname']['readOnly'] = True

    # save the changes, if any
    if request.method == 'POST':
        if request.POST.get('changes'):
            errors = handsontable_generic_save(json.loads(request.POST['changes']), table_cols, MODEL)
            if errors:
                return JsonResponse({'errors': errors})

    search_term = request.GET.get('q') or ''

    query = MODEL.objects.order_by('id')
    if search_term:
        query = query.filter(rname__icontains=search_term)
    if request.GET.get('id__exact'):
        query = query.filter(id=request.GET.get('id__exact'))
        logging.debug(query.query)
    query = query[:HANDSONTABLE_MAX_ROWS]
    table_data = []
    for rec in query:
        # convert the orm record "rec" into the dict "row", processing foreignkey and choice fields
        table_data.append(handsontable_process_rows(rec, table_cols, table_cols_idx_by_name))
    logging.debug('handsontable... table response #recs=%s', len(table_data))

    # if we were just loading the data, skip the rest and return the json table data only
    if request.method == 'POST':
        return HttpResponse(json.dumps({'table_data': table_data}, cls=DjangoJSONEncoder), content_type='application/json')

    context = RequestContext(request)
    context['search_term'] = search_term or ''
    context['SPECIAL_PREFIX'] = HANDSONTABLE_FIELD_PREFIX
    context['MAX_ROWS'] = HANDSONTABLE_MAX_ROWS
    context['link_list'] = reverse('spreadsheet_' + model_name)
    context['title'] = model_name
    context['table_data'] = json.dumps(table_data, cls=DjangoJSONEncoder)
    context['table_columns'] = json.dumps([x for x in table_cols if x['type'] != 'hidden'])

    return render_to_response("spreadsheet_demo.html", context)
