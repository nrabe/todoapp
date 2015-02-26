# -*- coding: utf-8 -*-
import logging
import json
from collections import OrderedDict  # @UnresolvedImport
import datetime

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.admin.views.decorators import staff_member_required
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.loading import get_model
from django.utils import timezone


# dt_server_now, dt_server_to_local, dt_local_to_server, dt_string_to_server, model_tools

HANDSONTABLE_FIELD_PREFIX = '_hOt_'  # temporary ID prefix for new records, and prefix for special field values.
HANDSONTABLE_MAX_ROWS = 100

FIELDNAME_PK = 'pk'
FIELDNAME_ORDERBY = '-date_created'
SKIP_FIELDS = ('date_created', 'date_updated',
               'creation_date', 'last_update', 'rec_status', 'is_test',
               'rna1me', 'password', 'private_dining_room', 'payment_notes')


def model_to_definition(MODEL):
    model_name = MODEL._meta.model_name
    app_name = MODEL._meta.app_label

    #
    # very simple automatic column definition
    #
    table_cols = []
    for field in MODEL._meta.fields:
        if field.name in SKIP_FIELDS:
            continue
        skip_choices = False
        coldef = {"data": field.name,
                  "label": unicode(field.verbose_name),
                  "type": "text",
        }
        if not field.blank:
            coldef['required'] = True
        if field.null:
            coldef['nullable'] = True

        if field.primary_key:
            coldef['data'] = 'pk'
            coldef['readOnly'] = True
            coldef['renderer'] = 'detaillink_Renderer'
            coldef['extra_links'] = []
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
        elif isinstance(field, models.IntegerField):
            coldef['type'] = 'numeric'
        elif isinstance(field, models.DecimalField):
            coldef['format'] = '0,0.00'
            coldef['type'] = 'numeric'
        elif isinstance(field, models.ForeignKey):
            coldef['type'] = 'foreignkey'
            coldef['fieldname'] = coldef['data'] + '_id'
            try:
                coldef['link_to'] = reverse('spreadsheet_%s' % (field.rel.to._meta.model_name)) + '?id__exact=%28val%29'
            except NoReverseMatch, e:
                logging.error(e)
                try:
                    coldef['link_to'] = reverse('admin:%s_%s_change' % (app_name, field.rel.to._meta.model_name),
                                                args=['(val)'])
                except NoReverseMatch, e:
                    logging.error(e)
            coldef['lookup_remote_url'] = reverse('handsontable_generic_autocomplete', kwargs={
                'app_name': app_name,
                'model_name': field.rel.to._meta.model_name,
                'field_name': coldef['fieldname']})
        # elif isinstance(field, tablenow.backend2.model_tools.MultiSelectField):
        # table_cols.append({'data': coldef['data'], 'type': 'hidden'})
        # coldef['type'] = 'multiselect'
        # coldef['fieldname'] = coldef['data']
        # #            coldef['data'] += '__L'
        # #            coldef['lookup_choices'] = OrderedDict([(unicode(k), v) for k, v in field.choices])
        #             skip_choices = True
        elif isinstance(field, models.CharField):
            coldef['type'] = 'text'
        elif isinstance(field, models.TextField):
            coldef['type'] = 'text'
        elif isinstance(field, models.AutoField):
            coldef['type'] = 'text'
        else:
            logging.warn('handsontable_generic_view() skipping field %s (could not determine type for %s)', field.name,
                         field.__class__)
        if field.choices and not skip_choices:
            coldef['subtype'] = coldef['type']
            coldef['type'] = 'lookup'
            coldef['lookup_choices'] = OrderedDict(field.choices)

        if field.name in ('rname',):
            coldef['copyable'] = False

        table_cols.append(coldef)
    # prepare some indexes for fast access to column defs
    table_cols_idx_by_name = {d['data']: d for d in table_cols}

    extra_links = []
    for l in [rel for rel in MODEL._meta.get_all_related_objects()]:
        try:
            u = reverse('spreadsheet_%s' % (l.opts.model_name,)) + '?%s_id__exact=%%(val)s' % (l.field.name,)
            extra_links.append((l.opts.model_name, u))
        except NoReverseMatch as e:
            logging.warn(e)

    # override some of the automatic definitions
    table_cols_idx_by_name['pk']['extra_links'] = extra_links

    try:
        table_cols_idx_by_name['pk']['link_to'] = reverse('admin:%s_%s_change' % (app_name, model_name), args=['(val)'])
    except NoReverseMatch as e:
        logging.warn('Could not find detail page for %s', model_name)
    table_cols_idx_by_name['pk']['link_to'] = '#'

    return table_cols, table_cols_idx_by_name


def handsontable_process_rows(rec, table_cols, table_cols_idx_by_name):
    """  pre-process each row according to the column definition """

    row = {k['data']: getattr(rec, k['data']) for k in table_cols
           if not k['data'].endswith('__L') and not k.get('writeOnly')}
    pk = row.get(FIELDNAME_PK)
    assert pk, 'row without pk? %r' % row

    for coldef in table_cols:
        if coldef['type'] == 'foreignkey':
            key = getattr(rec, coldef['fieldname'])
            label = getattr(rec, coldef['data'])
            label = label is not None and unicode(label) or None
            row[coldef['data']] = {'k': key, 'l': label}
        elif coldef.get('lookup_choices'):
            key = (getattr(rec, coldef['data']))
            label = coldef['lookup_choices'].get(key, None)
            row[coldef['data']] = {'k': key, 'l': label}
        elif coldef['type'] == 'multiselect':
            row[coldef['data']] = ', '.join(getattr(rec, coldef['fieldname']) or [])
    return row


_parse_datetime_from_js_formats = [
    (2, '%a %d %b, %Y %I:%M %p %z'),
    (2, '%a %d %b, %Y %I:%M %p %Z'),
    (1, '%a %d %b, %Y'),
    (2, '%Y-%m-%dT%H:%M:%S.%fz'),
    (2, '%Y-%m-%dT%H:%M:%S.%fZ'),
    (1, '%Y-%m-%d'),
    (0, 'H:%M:%S.%fz'),
    (0, '%H:%M:%S.%fZ'),
    (0, 'H:%Mz'),
]


def _parse_datetime_from_js(v):
    if v:
        t = None
        for d, f in _parse_datetime_from_js_formats:
            try:
                t = datetime.datetime.strptime(v, f)
                break
            except:
                pass
        if not t:
            raise ValueError("could not parse date: %r" % v)
        t = timezone.make_aware(t, timezone.utc)
        if d == 2:
            return t
        elif d == 1:
            return t.date()
        elif d == 0:
            return t.time()
    return None


def handsontable_process_change(change, table_cols):
    """  validates and process the the changes to be made the record """

    values = {k: v for k, v in change.items() if not k.startswith(HANDSONTABLE_FIELD_PREFIX)}
    pk = values.pop('pk', None)
    assert pk is not None, 'a change without an pk? %r' % change
    if str(pk).startswith(HANDSONTABLE_FIELD_PREFIX + '_pk__'):
        pk = None  # new record
    if change.get(HANDSONTABLE_FIELD_PREFIX + '_flag_delete_record__'):
        assert pk is not None, 'a delete without an pk? %r' % change
        return pk, True, None
    for coldef in table_cols:
        name = coldef['data']
        if name in values:
            if coldef.get('nullable') and values[name] in ('', u'', None):
                values[name] = None
            if coldef['type'] == 'checkbox':
                values[name] = values[name] in ('True', 'true', u'True', u'true', True)
            elif coldef['type'] == 'numeric':
                try:
                    values[name] = float(values[name])
                except Exception, e:
                    logging.warn(e)
            elif coldef.get('lookup_choices'):
                if coldef['subtype'] == 'numeric':
                    values[name] = values[name] and int(values[name]) or None
            elif coldef['type'] in ('datetime', 'date', 'time'):
                if name in values:
                    s = values[name]
                    values[name] = _parse_datetime_from_js(values[name])
    return pk, False, values


def handsontable_generic_save(changes, table_cols_ids, modelClass):
    """ create/update/delete of each change in "changes". Most of the code is devoted to error handling. """

    logging.info('handsontable_generic_save() saving #%s changes', len(changes))
    errors = []
    new_record_ids = {}
    # NOTE: I'm not sure this is the right way to handle transactions in the new Django 1.6+ way...
    # it says never catch an exception inside atomic()
    # but we *need* to catch and store errors on a per-record basis, to send back to the page.

    for change in changes:
        pk = None
        values = None
        last_field = None
        try:
            pk, delete, values = handsontable_process_change(change, table_cols_ids)
            if not pk:
                rec = modelClass()
            else:
                rec = modelClass.objects.get(pk=pk)
                if delete:
                    rec.delete()
                    continue
            for last_field, v in values.items():
                setattr(rec, last_field, v)
            rec.full_clean()
            rec.save()
            if not pk:
                new_record_ids[change.get('pk')] = rec.id
        except (ValidationError, ValueError) as e:
            logging.error('handsontable_XXX_save() pk=%s validation=%r change=%r', pk, e, change)
            temp = getattr(e, 'error_dict', {})
            if temp:
                for fn, fe in temp.items():
                    logging.warn([fn, values and values.get(fn), repr(fe), change])
                    errors.append({'error': repr(fe), 'field': fn, 'item': change})
            else:
                temp = getattr(e, 'messages', [])
                if temp:
                    for fe in e.messages:
                        errors.append({'error': repr(fe), 'item': change})
                else:
                    errors.append({'error': repr(e), 'item': change})
            flag_error = True
    return errors, new_record_ids


@staff_member_required
def handsontable_generic_autocomplete_view(request, app_name, model_name, field_name):
    """ general autocomplete for all models: it searches/shows the rname field only. """

    MAX_ROWS = 20
    model = get_model(app_name, model_name)
    search_term = request.GET.get('query') or ''
    if model_name == 'userprofile':
        query = model.objects.order_by('email')
        if search_term:
            query = query.filter(email__icontains=search_term)
    else:
        query = model.objects.order_by('rname')
        if search_term:
            query = query.filter(rname__icontains=search_term)
    logging.debug('handsontable_generic_autocomplete_view() query=%s', query.query)
    query = query[:MAX_ROWS]
    items = [{'pk': e.id, 'text': unicode(e)} for e in query]
    return JsonResponse({'items': items}, safe=False)


@staff_member_required
def handsontable_generic_view(request, app_name=None, model_name=None, TEMPLATE="handsontable_base.html"):
    """ defines/displays any model spreadsheet. Not really useful, you should always create a custom view per model """

    MODEL = get_model(app_name, model_name)

    table_cols, table_cols_idx_by_name = model_to_definition(MODEL)

    try:
        table_cols_idx_by_name['pk']['link_to'] = reverse('admin:%s_%s_change' % (app_name, model_name), args=['(val)'])
    except NoReverseMatch as e:
        logging.warn('Could not find detail page for %s', model_name)
    table_cols_idx_by_name['pk']['link_to'] = '#'

    new_record_ids = {}
    #
    # save the changes, if any
    #
    if request.method == 'POST':
        if request.POST.get('changes'):
            errors, new_record_ids = handsontable_generic_save(json.loads(request.POST['changes']), table_cols, MODEL)
            if errors:
                return JsonResponse({'errors': errors})

    search_term = request.GET.get('q') or ''

    query = MODEL.objects.order_by(FIELDNAME_ORDERBY)
    if search_term:
        query = query.filter(rname__icontains=search_term)
    for k, v in request.GET.items():
        if k.endswith('__exact'):
            query = query.filter(**{k: v})
    query = query[:HANDSONTABLE_MAX_ROWS]
    table_data = []
    for rec in query:
        # convert the orm record "rec" into the dict "row", processing foreignkey and choice fields
        table_data.append(handsontable_process_rows(rec, table_cols, table_cols_idx_by_name))
    logging.debug('handsontable... table response #recs=%s', len(table_data))

    # if we were just loading the data, skip the rest and return the json table data only
    if request.method == 'POST':
        resp = {'table_data': table_data}
        if new_record_ids:
            resp['new_record_ids'] = new_record_ids
        return HttpResponse(json.dumps(resp, cls=DjangoJSONEncoder), content_type='application/json')

    context = RequestContext(request)
    context['search_term'] = search_term or ''
    context['SPECIAL_PREFIX'] = HANDSONTABLE_FIELD_PREFIX
    context['MAX_ROWS'] = HANDSONTABLE_MAX_ROWS
    context['link_list'] = reverse('spreadsheet_' + model_name)
    context['title'] = model_name
    context['table_data'] = json.dumps(table_data, cls=DjangoJSONEncoder, indent=2)
    context['table_columns'] = json.dumps([x for x in table_cols if x['type'] != 'hidden'], cls=DjangoJSONEncoder,
                                          indent=2)

    return render_to_response(TEMPLATE, context)
