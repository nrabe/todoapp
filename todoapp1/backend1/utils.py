# -*- coding: utf-8 -*-
import logging
import datetime
import hashlib

from django.conf.urls import patterns, url

from django.utils import timezone
from django.templatetags.tz import localtime, do_timezone
from django.utils.log import AdminEmailHandler


class ThrottledAdminEmailHandler(AdminEmailHandler):
    PERIOD_LENGTH_IN_SECONDS = 300
    MAX_EMAILS_IN_PERIOD = 1

    def emit(self, record):
        throttle_name = 'ThrottledAdminEmailHandler' + hashlib.md5(repr(record.getMessage())).hexdigest()[:240]

        from django.core.cache import get_cache

        cache = get_cache("default")
        try:
            cache.incr(throttle_name)
        except ValueError:
            cache.set(throttle_name, 1, self.PERIOD_LENGTH_IN_SECONDS)
        counter = cache.get(throttle_name)

        if counter > self.MAX_EMAILS_IN_PERIOD:
            return
        super(ThrottledAdminEmailHandler, self).emit(record)


def LOG(level='debug', type='general', category='debug', exception=None, request=None, message=None, via_db=False,
        via_mail=False):
    """
    :param level: debug/info/warning/error/critical
    :param type: general/api/test/process.X
    :param category: success/failure/notice/none
    :param exception:
    :param request: request object. path/user/version and other values may be extracted. If not given, it'll try to guess using todoapp1.middleware.get_request()
    :param message: message to log. If it's an object, a suitable representation will be generated.
    :param via_db:
    :param via_mail:
    :return:
    """
    if not request:
        try:
            import todoapp1.middleware

            request = todoapp1.middleware.get_request()
        except:
            pass
    msg = '[%s %s] %s %r' % ( type, category, message, exception and exception or '')
    levels = {"debug": 10, "info": 20, "warning": 30, "error": 40, "critical": 50}
    logging.log(levels.get(level) or 0, msg)
    if via_mail:
        logger = logging.getLogger('django.request')
        logger.exception(msg, extra={'status_code': 500, 'request': request})


def dt_server_now():
    """ UTC server and DB time """
    return timezone.now().replace(microsecond=0)


def dt_string_to_server(dt):
    """ parses/converts a date from utc to utc (datetime) """
    if isinstance(dt, (str, unicode)):
        dt = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
    t = dt.replace(tzinfo=timezone.utc)
    logging.debug('dt_local_to_server %r %r %r', dt, t, timezone.get_default_timezone())
    return t


def dt_local_to_server(dt):
    """ parses/converts a date from local to utc. Notice how we force the UTC timezone with .astimezone(timezone.utc)"""
    if isinstance(dt, (str, unicode)):
        dt = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
    t = do_timezone(dt, timezone.get_default_timezone()).astimezone(timezone.utc)
    logging.debug('dt_local_to_server %r %r', dt, t)
    return t


def dt_server_to_local(dt):
    """ parses/converts a date from utc to local """
    if isinstance(dt, (str, unicode)):
        dt = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
    return do_timezone(dt, timezone.get_current_timezone())
