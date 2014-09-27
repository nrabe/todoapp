# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView
from django.contrib.flatpages import views


class TextPlainView(TemplateView):
    def render_to_response(self, context, **kwargs):
        return super(TextPlainView, self).render_to_response(context, content_type='text/plain', **kwargs)


urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'todoapp1.web1.views.home', name='home'),
    url(r'^signup/$', 'todoapp1.web1.views.signup', name='signup'),
    url(r'^signin/$', 'todoapp1.web1.views.signin', name='signin'),
    url(r'^signout/$', 'todoapp1.web1.views.signout', name='signout'),
    url(r'^profile/$', 'todoapp1.web1.views.profile', name='profile'),
    url(r'^signout/$', 'todoapp1.web1.views.signout', name='signout'),

    url(r'^lists/$', 'todoapp1.web1.views.todo_lists', name='todo_lists'),
    url(r'^lists/view$', 'todoapp1.web1.views.todo_lists', name='todo_lists_detail'),

    url("^robots.txt$", TextPlainView.as_view(template_name="robots.txt")),

    url(r'^sys/test/500-internal-server-error/', 'todoapp1.web1.views.system_test_fatal', name='system_test_fatal'),
    url(r'^sys/test/', 'todoapp1.web1.views.system_test', name='system_test'),

    url(r'^about-us/$', views.flatpage, {'url': '/about-us/'}, name='about'),
    url(r'^contact-us/$', views.flatpage, {'url': '/contact-us/'}, name='contact-us'),
)
