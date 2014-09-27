# -*- coding: utf-8 -*-
import logging
from django.views.defaults import server_error as django_server_error
from django.views.defaults import page_not_found as django_page_not_found
from django import http


def server_error(request, template_name='errors/500.html'):
    logging.error('[500] %s %s', request.get_full_path(), request.META)
    if request.path.startswith('/api/'):
        return http.HttpResponseServerError('{}', content_type='application/json')
    return django_server_error(request, template_name)


def page_not_found(request):
    logging.warn('[404] %s %s', request.get_full_path(), request.META)
    if request.path.startswith('/api/'):
        return http.HttpResponseNotFound('{}', content_type='application/json')
    return django_page_not_found(request)


"""
Wrapper for loading templates from "templates" directories in INSTALLED_APPS
packages, prefixed by the appname for namespacing.

This loader finds `appname/templates/index.html` when looking for something
of the form `appname/index.html`.
"""
import os
from django.template import TemplateDoesNotExist
from django.template.loaders.app_directories import app_template_dirs, Loader as BaseAppLoader


class Loader(BaseAppLoader):
    '''
    Modified AppDirectory Template Loader that allows namespacing templates
    with the name of their app, without requiring an extra subdirectory
    in the form of `appname/templates/appname`.
    '''
    def load_template_source(self, template_name, template_dirs=None):
        try:
            app_name, template_path = template_name.split('/', 1)
        except ValueError:
            raise TemplateDoesNotExist(template_name)

        if not template_dirs:
            template_dirs = (d for d in app_template_dirs if d.endswith('%(sep)s%(app_name)s%(sep)stemplates' % {'sep': os.sep, 'app_name': app_name}))

        return iter(super(Loader, self).load_template_source(template_path, template_dirs))
