# -*- coding: utf-8 -*-
import logging
import sys
import time
import datetime
import decimal
import json

from bunch import bunchify

from django.http import JsonResponse
from django.conf import settings
from django.test.client import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_control
from django.core.validators import validate_email
from django.core.management import call_command
from error_messages import ERRORS

__all__ = [
           'ApiException',
           'param_string',
           'param_integer',
           'param_latlon',
           'param_email',
           'get_api_context',
           'api_call',
           'jsonrpc_dispatcher',
           ]


class ApiException(Exception):
    message = None
    code = None
    data = None

    def __init__(self, code=100, message=None, data=None, extra_info=None):
        super(ApiException, self).__init__(message, code, data)
        self.message = message
        self.code = code
        self.data = data
        self.extra_info = extra_info

    def __repr__(self):
        return 'ApiException(message=%s, code=%s, data=%s)' % (self.message, self.code, self.data)


def set_cookie(response, key, value, days_expire=7):
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60  # one year
    else:
        max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)


def param_string(val, required=False, blank=True, max_size=255, error=ERRORS.invalid_parameter, field_name=None, after=None):
    error = ApiException(error[0], error[1] % {'field_name': field_name, 'val': val})
    if val is None:
        if required:
            raise error
        return None
    elif not val.strip() and not blank:
        raise error
    val = unicode(val).strip()
    if len(val) > max_size:
        raise error
    if after:
        return after(val)
    return val


def param_integer(val, required=False, blank=True, error=ERRORS.invalid_parameter, field_name=None, after=None):
    error = ApiException(error[0], error[1] % {'field_name': field_name, 'val': val})
    if val is None:
        if required:
            raise error
        return None
    elif not val and not blank:
        raise error
    try:
        val = int(val)
    except:
        raise error
    if after:
        return after(val)
    return val


def param_email(val, required=False, blank=True, error=ERRORS.invalid_parameter, field_name=None, after=None):
    error = ApiException(error[0], error[1] % {'field_name': field_name, 'val': val})
    if val is None:
        if required:
            raise error
        return val
    if not val and not blank:
        raise error
    try:
        validate_email(val)
    except Exception:
        raise error
    if after:
        return after(val)
    return val


def param_latlon(lat, lon, required=False, error=ERRORS.invalid_parameter, field_name=None, after=None):
    error = ApiException(error[0], error[1] % {'field_name': field_name, 'val': (lat, lon)})
    if (lat is None) or (lon is None):
        if required:
            raise error
        return None, None
    try:
        lat, lon = decimal.Decimal(lat), decimal.Decimal(lon)
    except:
        raise error
    return lat, lon


def get_curr_user(request, required=False):
    """ this function has two "special" features it'd be best to avoid (but could not find a nicer way)
        1) the local import part, and
        2) the transformation form django.auth.User to models.UserProfile
    """
    from models import UserProfile
    if not request.user.is_authenticated():
        if required:
            raise ApiException(*ERRORS.authentication_required)
        return None
    curr_user = request.user
    curr_user.__class__ = UserProfile
    return curr_user


def get_api_context(client_version='PYTHON.1.0.0', sessionid=None, request=None):
    if request:
        sessionid = sessionid or request.session.get('api_sessionid')
    request = RequestFactory().get('/')
    if sessionid:
        request.COOKIES[settings.SESSION_COOKIE_NAME] = sessionid
    if not 'session' in request:
        SessionMiddleware().process_request(request)
        request.session.save()
    AuthenticationMiddleware().process_request(request)
    request.x_is_python_native = True
    request.META['X-CLIENT-VERSION'] = client_version
    return request


registered_api_calls = {}


def api_call(func):
    """
    Decorator to log each API call, to perform certain common functions, such as logging, serializing, client version parsing, etc.

    Function names should start with "api_"
    Any exception other than ApiException() is a fatal error (either a programming error or a runtime error).
    Parameters: Use only keyword values function( name=XXX ), not positional values function(XXX).
    Parameters: unexpected parameters will throw an ApiException()
    Parameters: validation and value parsing are manual, not automatic ( use the param_* functions )
    Parameters: the priority order is python native, HTTP POST and HTTP GET

    Do not rely too much on the request object (session, cookies, auth, GET, POST, path, etc)... it may be a fake request object ( when called from native python )
    """

    assert func.__name__.startswith('api_')
    registered_api_calls[func.__name__] = func

    def decorated(request, *args, **kwargs):
        assert not args, 'Please, use only keyword values function( name=XXX ), not positional values function(XXX)'
        _start_time = time.time()

        request.x_client_version = kwargs.pop('x_client_version', None) or request.META.get('X-CLIENT-VERSION', 'WEB.0.0.0').decode("utf-8")  # NOTE: version in the format: web.0.0.0
        request.x_is_python_native = getattr(request, 'x_is_python_native', False)
        request.x_post_response_tasks = []

        for key, val in request.POST.items() + request.GET.items():
            kwargs.setdefault(key, val)

        response, last_exception = None, None
        try:
            response = func(request, *args, **kwargs)
            if settings.USE_TASK_QUEUE:
                call_command('pqbenchmark')

            if request.x_is_python_native:
                return bunchify(response)
            return JsonResponse(response, safe=False)
        except TypeError, last_exception:
            # if it is an extra parameter to an api_* function, treat it as a non-fatal error
            if str(last_exception).startswith('api_'):
                raise ApiException(last_exception)
            raise  # fatal, unexpected error
        except Exception, last_exception:
            raise  # fatal, unexpected error
        finally:
            curr_user = get_curr_user(request, required=False)
            logging_params = ((time.time() - _start_time) * 1000, func.__name__,
                              ', '.join(['%s=%.512r' % (k, v) for k, v in kwargs.items()]), request.x_client_version,
                              curr_user and curr_user.email or '(anon)',
                              sys._getframe().f_back.f_code.co_name,
                              response or last_exception)
            if last_exception:
                logging.error('[ERR % 4dms] backend.%s(apicontext, %s) # ver=%s user=%s caller=%s() exception=%.1024r\n', *logging_params)
            elif settings.USE_API_LOGGING:
                logging.info('[API % 4dms] backend.%s(apicontext, %s) # ver=%s user=%s caller=%s() response=%.1024r\n', *logging_params)

    return decorated


@csrf_exempt
@cache_control(max_age=0, no_cache=True, no_store=True)
def jsonrpc_dispatcher(request, x_client_version=None):
    """ This is the JSONRPC dispatcher. All API calls via JSONRPC go through this method """
    _start_time = time.time()
    flag_single_call = False
    json_responses = []
    request.x_client_version = x_client_version
    try:
        json_requests = json.loads(request.body)
        if isinstance(json_requests, dict):
            json_requests = [json_requests]
            flag_single_call = True
    except Exception, e:
        json_responses = {"jsonrpc": "2.0", "id": "", 'error': {'code': (-32700), 'message': 'Parser error'}}
    if not json_responses:
        request.x_is_python_native = True
        logging.info('[RPC % 4dms %s calls]\n', (time.time() - _start_time) * 1000, len(json_requests))
        for req in json_requests:
            resp = {'id': req.get('id'), "jsonrpc": "2.0"}
            if (req.get("jsonrpc") != "2.0") or (req.get('id') is None) or (not req.get('method')):
                resp['error'] = {'code': (-32600), 'message': 'Invalid Request'}
            elif req['method'] not in registered_api_calls:
                resp['error'] = {'code': (-32601), 'message': 'Method not found'}
            else:
                try:
                    params = req.get('params') or {}
                    resp['result'] = api_call(registered_api_calls[req['method']])(request, **params)
                except ApiException, e:
                    resp['error'] = {'code': e.code or 100, 'message': e.message}
                except Exception, e:
                    resp['error'] = {'code': (-32000), 'message': 'Server error %s' % e}
            json_responses.append(resp)
    if flag_single_call:
        return JsonResponse(json_responses[0], safe=False)
    else:
        return JsonResponse(json_responses, safe=False)
