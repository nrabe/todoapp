# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib import admin

# for flatpages markdown
from django_markdown import flatpages
flatpages.register()

from .monkeypatch_flatpages import monkeypatch_flatpages
monkeypatch_flatpages()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/handsontable_users/', 'todoapp1.admin1.views.handsontable_users', name='handsontable_users'),
    url(r'^admin/handsontable_demo/', 'todoapp1.admin1.views.handsontable_demo', name='handsontable_demo'),
    url('^markdown/', include('django_markdown.urls')),
)
