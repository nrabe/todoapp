# -*- coding: utf-8 -*-
import time
import logging

from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.db import connection

from models import TODOList, TODOListItem, UserProfile
from error_messages import ERRORS
from api_utils import ApiException, api_call, param_string, param_integer, param_email, param_latlon, get_curr_user, get_api_context, jsonrpc_dispatcher  # @UnusedImport

import emails

@api_call
def api_sys_test(request, test=''):
    """ returns a list of configuration parameters ( server version, mood types, titles, etc )."""
    response_json = {}
    if test == 'fatal_error':
        raise NameError('this_method_does_not_exist')
    elif test == 'error':
        raise ApiException(100, 'Testing error handling')
    elif test == 'db_error':
        # this is *EXPECTED* to fail, badly
        cursor = connection.cursor()
        cursor.execute("UPDATE bar SET foo = 1 WHERE baz = %s", [1])
        cursor.execute("SELECT foo FROM bar WHERE baz = %s", [1])
    response_json['ok'] = 1
    return response_json


@api_call
def api_sys_create_test_data(request, also_remove=''):
    """
    removes and creates data for testing purposes, to be deleted by api_sys_remove_test_data.

    :param also_remove:
    """

    response_json = {}
    api_sys_remove_test_data(request)

    user1 = api_signup(request, email=settings.TEST_USER_1, password=settings.TEST_USER_PASSWORD, first_name='test1', last_name='test1')
    user2 = api_signup(request, email=settings.TEST_USER_2, password=settings.TEST_USER_PASSWORD, first_name='test2', last_name='test2')
    user3 = api_signup(request, email=settings.TEST_USER_3, password=settings.TEST_USER_PASSWORD, first_name='test3', last_name='test3')

    response_json['users'] = [user1, user2, user3]
    return response_json


@api_call
def api_sys_remove_test_data(request, also_remove=''):
    """
    removes the data created by api_sys_create_test_data and other testing processes.

    :param also_remove:
    """
    response_json = {}

    UserProfile.objects.filter(email__startswith=settings.TEST_USER_PREFIX).delete()

    if also_remove == 'mass':
        # due to sqlite limitations, we must delete in batches...
        while UserProfile.objects.filter(email__startswith=settings.TEST_USER_PREFIX2):
            logging.debug('mass users deleting...')
            ids = UserProfile.objects.filter(email__startswith=settings.TEST_USER_PREFIX2).values_list('pk', flat=True)[:100]
            UserProfile.objects.filter(pk__in=ids).delete()
    response_json['ok'] = 1
    return response_json


@api_call
def api_config(request):
    """
    returns a list of configuration parameters ( server version, mood types, titles, etc ).

    :param request:
    :return:
    """
    response_json = {}
    # response_json['mood_types'] = [{'moodtype': x.moodtype, 'title': x.title} for x in MoodType.objects.order_by('title')]
    response_json['photos_prefix'] = 'http://dummy.com/'
    return response_json


@api_call
def api_todolist(request, todolist_id=None, search=None, category=None):
    """
    returns one or more TO-DO Lists. At least one of the parameters is required.

    :param todolist_id:
    :param search:
    :param category:
    :return: :json:`{"todolists": [{"id": ""},]}`
    :raises ApiException: (200, 'Missing or invalid parameter FIELD_NAME VALUE')
    """

    curr_user = get_curr_user(request, required=True)

    search = param_string(search, required=False, blank=False, field_name='search')
    category = param_string(category, required=False, blank=False, field_name='category')
    todolist_id = param_integer(todolist_id, required=False, blank=False, field_name='todolist_id')

    if not (search or category or todolist_id):
        raise ApiException(*ERRORS.invalid_parameter)

    todolists = TODOList.list(search=search, category=category, curr_user=curr_user, todolist_id=todolist_id)

    response_json = {}
    response_json['todolists'] = [x.serialize() for x in todolists]
    return response_json


@api_call
def api_todolist_set(request, todolist_id=None, title=None, comments=None, category=None, status=None):
    """
    update or create a TO-DO List

    :param todolist_id: (optional when creating)
    :param title: (optional when updating)
    :param comments: (optional when updating)
    :param category: (optional when updating)
    :param status: (optional when updating)
    :return: :json:`{"todolist": {"id": ""}}`
    """

    curr_user = get_curr_user(request, required=True)

    title = param_string(title, required=True, blank=False, field_name='title')
    comments = param_string(comments, required=False, blank=True, field_name='comments')
    category = param_string(category, required=False, blank=True, field_name='category')
    status = param_integer(status, required=False, blank=True, field_name='status')
    todolist = param_integer(todolist_id, required=False, blank=False, field_name='todolist_id',
                         after=lambda todolist_id: TODOList.objects.get(pk=todolist_id))
    todolist = TODOList.upsert(title=title, comments=comments, category=category, status=status, curr_user=curr_user, todolist=todolist)

    response_json = {}
    response_json['todolist'] = todolist.serialize()
    return response_json


@api_call
def api_todolist_item_set(request, todolist_id=None, todolistitem_id=None, text=None, status=None):
    """ update or create a TO-DO List Item. Authentication required """

    curr_user = get_curr_user(request, required=True)

    text = param_string(text, required=True, blank=False, field_name='text')
    status = param_integer(status, required=False, blank=True, field_name='status')
    todolistitem = param_integer(todolistitem_id, required=False, blank=False, field_name='todolistitem_id',
                         after=lambda todolistitem_id: TODOListItem.objects.get(pk=todolistitem_id))
    todolist = None
    if not todolistitem:
        todolist = param_integer(todolist_id, required=True, blank=False, field_name='todolist_id',
                         after=lambda todolistitem_id: TODOList.objects.get(pk=todolist_id))
    todolistitem = TODOListItem.upsert(text=text, status=status, curr_user=curr_user, todolist=todolist, todolistitem=todolistitem)

    response_json = {}
    response_json['todolistitem'] = todolistitem.serialize()
    return response_json


@api_call
def api_todolist_share(request, todolist_id=None, share_with_email=None):
    """ share a TO-DO List. Authentication required """

    curr_user = get_curr_user(request, required=True)

    todolist = param_integer(todolist_id, required=True, blank=False, field_name='todolist_id',
                         after=lambda todolist_id: TODOList.objects.get(pk=todolist_id))
    shared_with = param_email(share_with_email, required=True, blank=False, field_name='shared_with_email',
                         after=lambda email: UserProfile.objects.get(email=email))

    todolist.share_with(curr_user=curr_user, shared_with=shared_with)

    response_json = {}
    response_json['todolist'] = todolist.serialize()
    return response_json


def _signin(request, email=None, password=None):
    """ performs the actual signing (or post-signup ) authentication """

    django_user = authenticate(username=email, password=password)
    if django_user is not None:
        login(request, django_user)
        request.session.save()
    else:
        raise ApiException(*ERRORS.signin_incorrect)
    # request.user = user
    assert request.user and request.user.is_authenticated()

    curr_user = get_curr_user(request)

    response_json = {}
    response_json['profile'] = curr_user.serialize_curr_user()
    response_json['sessionid'] = request.session.session_key
    return response_json


@api_call
def api_signup(request, email=None, password=None, first_name=None, last_name=None):
    """
    registers a new user and authenticates it

    :param email:
    :param password:
    :param first_name:
    :param last_name:
    :return: :json:`{"profile": {"id": ""}, "sessionid": ""}`
    :raises ApiException: (200, 'Missing or invalid parameter FIELD_NAME VALUE')
    :raises ApiException: (402, 'Invalid email address or password')
    :raises ApiException: (403, 'Email address already registered')
    """

    email = param_email(email, required=True, blank=False, field_name='email')
    password = param_string(password, required=True, blank=False, field_name='password')
    first_name = param_string(first_name, required=False, blank=False, field_name='first_name')
    last_name = param_string(last_name, required=False, blank=False, field_name='last_name')

    UserProfile.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name)
    response_json = _signin(request, email=email, password=password)

    curr_user = get_curr_user(request, required=True)
    emails.send_welcome_email(curr_user)

    return response_json


@api_call
def api_signin(request, email=None, password=None):
    """
    authenticates the user

    :param email:
    :param password:
    :return: :json:`{"profile": {"id": ""}, "sessionid": ""}`
    :raises ApiException: (200, 'Missing or invalid parameter FIELD_NAME VALUE')
    """
    response_json = _signin(request, email=email, password=password)
    return response_json


@api_call
def api_signout(request):
    """ clears the user session """
    response_json = {}
    logout(request)
    request.session.flush()
    return response_json


@api_call
def api_profile(request):
    """
    returns the current user profile ( just as signin/signup does ). Authentication required.

    :return: :json:`{"profile": {"id": ""}, "sessionid": ""}`
    :raises ApiException: (401, 'Authentication required')
    """
    curr_user = get_curr_user(request, required=True)

    response_json = {}
    response_json['profile'] = curr_user.serialize_curr_user()
    return response_json


@api_call
def api_profile_update(request, email=None, password=None, first_name=None, last_name=None):
    """
    updates and returns the current user profile. Authentication required.

    :return: :json:`{"profile": {"id": ""}, "sessionid": ""}`
    :raises ApiException: (401, 'Authentication required')
    :raises ApiException: (200, 'Missing or invalid parameter FIELD_NAME VALUE')
    :raises ApiException: (402, 'Invalid email address or password')
    :raises ApiException: (403, 'Email address already registered')
    """
    curr_user = get_curr_user(request, required=True)

    email = param_email(email, blank=False, field_name='email')
    password = param_string(password, blank=False, field_name='password')
    first_name = param_string(first_name, blank=False, field_name='first_name')
    last_name = param_string(last_name, blank=False, field_name='last_name')

    if email is not None:
        curr_user.email = email
    if password is not None:
        curr_user.set_password(password)
    if first_name is not None:
        curr_user.first_name = first_name
    if last_name is not None:
        curr_user.last_name = last_name
    curr_user.full_clean()
    curr_user.save()

    response_json = {}
    response_json['profile'] = curr_user.serialize_curr_user()
    return response_json
