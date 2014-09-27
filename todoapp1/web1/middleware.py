# -*- coding: utf-8 -*-
"""
GlobalRequestMiddleware: exposes the current request/user to any part of the app, by simply doing

from t8biz.middleware import get_request
request = get_request()

"""
import urllib
from threading import local
from django.conf import settings
from django.http import HttpResponse  # , HttpResponseRedirect
from django.utils.translation import ugettext as _

_active = local()


def get_request():
    return getattr(_active, 'request', None)


def get_user():
    return getattr(getattr(_active, 'request', None), 'user', None)


def get_is_test():
    try:
        return int(get_request().META.get('HTTP_X_IS_UNIT_TEST'))
    except:
        pass
    return 0


def set_request(request):
    """ this is used in unit-tests too """
    _active.request = request


class GlobalRequestMiddleware(object):
    def process_request(self, request):
        request.COOKIES2 = {k: urllib.unquote(v) for k, v  in request.COOKIES.items()}
        set_request(request)


def basic_challenge(realm=None):
    if realm is None:
        realm = getattr(settings, 'WWW_AUTHENTICATION_REALM', _('Restricted Access'))
    response = HttpResponse(_('Authorization Required'), content_type="text/plain")
    response['WWW-Authenticate'] = 'Basic realm="%s"' % (realm)
    response.status_code = 401
    return response


def basic_authenticate(authentication):
    (authmeth, auth) = authentication.split(' ', 1)
    if 'basic' != authmeth.lower():
        return None
    auth = auth.strip().decode('base64')
    username, password = auth.split(':', 1)
    return username == getattr(settings, 'BASIC_WWW_AUTHENTICATION_USERNAME') and password == getattr(settings, 'BASIC_WWW_AUTHENTICATION_PASSWORD')


class BasicAuthenticationMiddleware(object):
    def process_request(self, request):

        if not getattr(settings, 'BASIC_WWW_AUTHENTICATION', False):
            return

        # the api shouldn't go through basic auth
        if request.path.startswith('/api') or request.path.startswith('/admin'):
            return

        if request.META.get('HTTP_AUTHORIZATION') and basic_authenticate(request.META['HTTP_AUTHORIZATION']):
            return

        return basic_challenge()
