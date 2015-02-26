# -*- coding: utf-8 -*-
import logging
import json
from collections import OrderedDict  # @UnresolvedImport

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, JsonResponse
from django.db import models
from django.db.models import Q
from django.db.models.loading import get_model

from todoapp1.backend1.models import UserProfile, HandsontableDemo
from handsontable import handsontable_process_rows, handsontable_generic_save


@staff_member_required
def generic_autocomplete(request, app_name, model_name, field_name):
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
    logging.debug('generic_autocomplete() query=%s', query.query)
    query = query[:MAX_ROWS]
    items = [{'id': e.id, 'text': unicode(e)} for e in query]
    return JsonResponse({'items': items}, safe=False)


HANDSONTABLE_FIELD_PREFIX = '_hOt_'  # temporary ID prefix for new records, and prefix for special field values.
HANDSONTABLE_MAX_ROWS = 100


@staff_member_required
def spreadsheet_demo(request):
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
            coldef['lookup_remote_url'] = reverse('generic_autocomplete', kwargs={
                                                                                  'app_name': 'backend1',
                                                                                  'model_name': 'userprofile',
                                                                                  'field_name': coldef['fieldname']})
        elif isinstance(field, models.IntegerField):
            coldef['type'] = 'numeric'
        elif isinstance(field, models.DecimalField):
            coldef['format'] = '$0,0.00'
            coldef['type'] = 'numeric'
        if field.choices:
            table_cols.append({'data': coldef['data'], 'type': 'hidden'})
            coldef['type'] = 'lookup'
            coldef['fieldname'] = coldef['data']
            coldef['data'] += '__L'
            coldef['lookup_choices'] = OrderedDict(field.choices)
    # prepare some indexes for fast access to column defs
    table_cols_idx_by_name = {d['data']: d for d in table_cols}

    # override some of the automatic definitions
    table_cols_idx_by_name['id']['readOnly'] = True
    table_cols_idx_by_name['id']['renderer'] = 'detaillink_Renderer'  # special renderer to display a link to the detail page
    table_cols_idx_by_name['id']['detail_url'] = reverse('admin:backend1_handsontabledemo_change', args=['(id)'])
    table_cols_idx_by_name['rname']['readOnly'] = True

    #
    # save and/or retrieve the data, applying filters and options
    #
    if request.method == 'POST':
        if request.POST.get('changes'):
            errors = handsontable_generic_save(json.loads(request.POST['changes']), table_cols, HandsontableDemo)
            if errors:
                return JsonResponse({'errors': errors})
        query = HandsontableDemo.objects.order_by('id')
        if search_term:
            query = query.filter(email__icontains=search_term)
        query = query[:HANDSONTABLE_MAX_ROWS]
        table_data = []
        for rec in query:
            # convert the orm record "rec" into the dict "row", processing foreignkey and choice fields
            row = handsontable_process_rows(rec, table_cols, table_cols_idx_by_name)
            table_data.append(row)
        logging.debug('handsontable... table response #recs=%s', len(table_data))
        return HttpResponse(json.dumps({'table_data': table_data}, cls=DjangoJSONEncoder), content_type='application/json')

    context['SPECIAL_PREFIX'] = HANDSONTABLE_FIELD_PREFIX
    context['MAX_ROWS'] = HANDSONTABLE_MAX_ROWS
    context['link_list'] = reverse('spreadsheet_demo')
    context['table_columns'] = json.dumps([x for x in table_cols if x['type'] != 'hidden'])

    return render_to_response("spreadsheet_demo.html", context)


@staff_member_required
def spreadsheet_userprofile(request):
    """ defines/displays any model spreadsheet. Not really useful, you should always create a custom view per model """

    table_cols = [
                  {"data": "id", "label": "id", "type": "text", "readOnly": True,
                        'renderer': 'detaillink_Renderer',
                        'link_to': reverse('admin:backend1_userprofile_change', args=['(val)']),
                   },
                  {"data": "email", "label": "email", "type": "text"},
                  {"data": "first_name", "label": "first_name", "type": "text"},
                  {"data": "last_name", "label": "last_name", "type": "text"},
                  {"data": "is_active", "label": "is_active", "type": "checkbox"},
                  {"data": "is_staff", "label": "is_staff", "type": "checkbox"},
                  {"data": "last_login", "label": "last_login", "type": "datetime", 'readOnly': True},
                  {"data": "date_joined", "label": "date_joined", "type": "datetime", 'readOnly': True},
                  ]
    table_cols_idx_by_name = {d['data']: d for d in table_cols}

    # save the changes, if any
    if request.method == 'POST':
        if request.POST.get('changes'):
            errors = handsontable_generic_save(json.loads(request.POST['changes']), table_cols, UserProfile)
            if errors:
                return JsonResponse({'errors': errors})

    search_term = request.GET.get('q') or ''

    query = UserProfile.objects.order_by('first_name', 'last_name')
    if search_term:
        query = query.filter(Q(email__icontains=search_term) | Q(first_name__icontains=search_term) | Q(last_name__icontains=search_term))
    if request.GET.get('id__exact'):
        query = query.filter(id=request.GET.get('id__exact'))
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
    context['link_list'] = reverse('spreadsheet_userprofile')
    context['title'] = 'userprofile'
    context['table_data'] = json.dumps(table_data, cls=DjangoJSONEncoder)
    context['table_columns'] = json.dumps([x for x in table_cols if x['type'] != 'hidden'])

    return render_to_response("spreadsheet_userprofile.html", context)
