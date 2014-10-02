# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',
    url(r'^m/', include('todoapp1.mobile1.urls', 'mobile')),
    url(r'^p/', include('django.contrib.flatpages.urls', 'content_pages')),
    url(r'^api/', include('todoapp1.backend1.urls', 'api')),
    url(r'^', include('todoapp1.web1.urls')),
)
# from todoapp1.admin1.urls import urlpatterns as admin_urlpatterns
urlpatterns += patterns('',
    url(r'^admin/', include('todoapp1.admin1.urls', app_name='admin')),
)

# In debug mode (DEV, LOCAL), process and log 404 and 500 errors (with DEBUG=False 404's will be ignored and 500's will be sent by email)
if settings.DEBUG:
    handler404 = 'todoapp1.web1.django_utils.page_not_found'
    handler500 = 'todoapp1.web1.django_utils.server_error'
