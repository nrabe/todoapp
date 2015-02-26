# -*- coding: utf-8 -*-

import os
import sys
import datetime

sys.path.append(os.path.abspath('./'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "todoapp1.settings." + os.environ.get("ENVIRONMENT", "MUST-SET-ENVIRONMENT-VARIABLE-SEE-README"))
import django
django.setup()

from django.conf import settings
from todoapp1.backend1 import api as backend

from django.utils import timezone
from django.templatetags.tz import localtime

from todoapp1.backend1.utils import dt_server_now, dt_server_to_local, dt_local_to_server

print 'USE_TZ', settings.USE_TZ
print 'DEFAULT TIMEZONE', settings.TIME_ZONE
print 'get_current_timezone()', timezone.get_current_timezone_name(), timezone.get_current_timezone()
print 'get_default_timezone()', timezone.get_default_timezone_name(), timezone.get_default_timezone()

NOW = dt_server_now()
NOW_DT = NOW
NOW_STR = NOW_DT.strftime("%Y-%m-%dT%H:%M:%S")
NOWL_DT = dt_server_to_local(NOW)
NOWL_STR = dt_server_to_local(NOW).strftime("%Y-%m-%dT%H:%M:%S")

print '1. SERVER NOW_DT ', NOW_DT
print '1. SERVER NOW_STR', NOW_STR
print '1. LOCAL NOW_DT  ', NOWL_DT
print '1. LOCAL NOW_STR ', NOWL_STR


print '2. LOCAL NOWL_STR', NOWL_STR
print '2. SERVER NOW_DT ', dt_local_to_server(NOWL_STR)
print '2. SERVER NOW_STR', dt_local_to_server(NOWL_STR).strftime("%Y-%m-%dT%H:%M:%S")
print '2. LOCAL NOW_DT  ', dt_server_to_local(NOWL_STR)
print '2. LOCAL NOW_STR ', dt_server_to_local(NOWL_STR).strftime("%Y-%m-%dT%H:%M:%S")


print 'dt_server_now()        server=', NOW.isoformat()
print 'dt_server_to_local()   local =', dt_server_to_local(NOW).isoformat()
print 'dt_local_to_server()   server=', dt_local_to_server(NOW).isoformat()

timezone.activate(timezone.get_default_timezone())

print 'dt_server_now()        ', NOW.isoformat()
print 'dt_server_to_local()   ', dt_server_to_local(NOW).isoformat()
print 'dt_local_to_server()   ', dt_local_to_server(NOWS).isoformat()

