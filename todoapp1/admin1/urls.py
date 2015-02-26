# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib import admin

# for flatpages markdown
from django_markdown import flatpages
flatpages.register()

from .monkeypatch_flatpages import monkeypatch_flatpages
monkeypatch_flatpages()

urlpatterns = patterns('',
    url(r'^generic_autocomplete/(?P<app_name>.+)/(?P<model_name>.+)/(?P<field_name>.+)/', 'todoapp1.admin1.views.generic_autocomplete', name='generic_autocomplete'),


    url(r'^spreadsheet_demo/', 'todoapp1.admin1.views.spreadsheet_demo', name='spreadsheet_demo'),
    url(r'^spreadsheet_demo1/', 'todoapp1.admin1.handsontable.handsontable_generic_view',
        name='spreadsheet_handsontabledemo', kwargs={'app_name': 'backend1', 'model_name': 'handsontabledemo'}),

    url(r'^spreadsheet_userprofile/', 'todoapp1.admin1.views.spreadsheet_userprofile', name='spreadsheet_userprofile'),

    url(r'^spreadsheet/backend1/todolist/', 'todoapp1.admin1.handsontable.handsontable_generic_view', name='spreadsheet_todolist', kwargs={'app_name': 'backend1', 'model_name': 'todolist'}),
    url(r'^spreadsheet/backend1/todolistitem', 'todoapp1.admin1.handsontable.handsontable_generic_view', name='spreadsheet_todolistitem', kwargs={'app_name': 'backend1', 'model_name': 'todolist'}),

    url(r'^handsontable_generic_autocomplete/(?P<app_name>.+)/(?P<model_name>.+)/(?P<field_name>.+)/',
       'todoapp1.admin1.handsontable.handsontable_generic_autocomplete_view', name='handsontable_generic_autocomplete'),

    # url(r'^handsontable_demo/autocomplete/(?P<fieldname>.+)/', 'todoapp1.admin1.views.handsontable_demo_autocomplete', name='handsontable_demo_autocomplete'),
    # url(r'^handsontable_demo/', 'todoapp1.admin1.views.handsontable_demo', name='handsontable_demo'),

    url('^markdown/', include('django_markdown.urls')),
    url(r'^', include(admin.site.urls)),
)
