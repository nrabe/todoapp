# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url


def url_v1(u, funcName):
    return url("^0.1/(?P<x_client_version>[a-zA-Z0-9\.]+)/%s/" % u, 'todoapp1.backend1.api.%s' % funcName, name=funcName)


urlpatterns = patterns('',
    url(r'^0.1/jsonrpc/v1/(?P<x_client_version>[a-zA-Z0-9\.]+)/$', 'todoapp1.backend1.api.jsonrpc_dispatcher', name='jsonrpc'),

    url_v1(r'sys/test', 'api_sys_test'),
    url_v1(r'sys/remove_test_data', 'api_sys_remove_test_data'),

    url_v1(r'config', 'api_config'),

    url_v1(r'todolist/set$', 'api_todolist_set'),
    url_v1(r'todolist/item/set', 'api_todolist_item_set'),
    url_v1(r'todolist/share', 'api_todolist_share'),
    url_v1(r'todolist/', 'api_todolist'),

    url_v1(r'profile/update', 'api_profile_update'),
    url_v1(r'profile', 'api_profile'),
    url_v1(r'signup', 'api_signup'),
    url_v1(r'signin', 'api_signin'),
    url_v1(r'signout', 'api_signout'),
)
