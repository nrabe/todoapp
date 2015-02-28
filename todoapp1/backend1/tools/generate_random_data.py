# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.abspath('./'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "todoapp1.settings." + os.environ.get("ENVIRONMENT", "MUST-SET-ENVIRONMENT-VARIABLE-SEE-README"))
import django
django.setup()

from django.conf import settings
from todoapp1.backend1 import api as backend

from todoapp1.settings.constants import TEST_USER_EMAIL_FORMAT, TEST_USER_PASSWORD

apicontext1 = backend.get_api_context()

backend.api_sys_remove_test_data(apicontext1, also_remove='mass')
print 'starting...'

settings.PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
settings.USE_API_LOGGING = False
 
for i in range(0, 100):
    if i % 100 == 0:
        print 'mass users creating batch# %s' % i
    try:
        backend.api_signup(apicontext1, email=TEST_USER_EMAIL_FORMAT % i, password=TEST_USER_PASSWORD, first_name='test%s' % i, last_name='test%s' % i)
    except backend.ApiException, e:
        assert e.code == backend.ERRORS.signup_email_already_exists[0]
 
    response = backend.api_todolist_set(apicontext1, title='test1-%s' % i)
    todolist1 = response['todolist']
    response = backend.api_todolist_item_set(apicontext1, todolist_id=todolist1.id, text='test1-1-%s' % i)
    response = backend.api_todolist_item_set(apicontext1, todolist_id=todolist1.id, text='test1-2-%s' % i)
    response = backend.api_todolist_item_set(apicontext1, todolist_id=todolist1.id, text='test1-3-%s' % i)
 
    response = backend.api_todolist_set(apicontext1, title='test2-%s' % i)
    todolist1 = response['todolist']
    response = backend.api_todolist_item_set(apicontext1, todolist_id=todolist1.id, text='test2-1-%s' % i)
    response = backend.api_todolist_item_set(apicontext1, todolist_id=todolist1.id, text='test2-2-%s' % i)
    response = backend.api_todolist_item_set(apicontext1, todolist_id=todolist1.id, text='test2-3-%s' % i)
