# -*- coding: utf-8 -*-
import logging

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib import messages

from todoapp1.backend1 import api as backend


def home(request):
    apicontext = backend.get_api_context(request=request)
    context = RequestContext(request)

    response = backend.api_config(apicontext)
    context['photos_prefix'] = response['photos_prefix']
    return render(request, "index.html", context_instance=context)


def signup(request):
    apicontext = backend.get_api_context(request=request)

    email = request.POST.get('email')
    password = request.POST.get('password')
    first_name = request.POST.get('last_name')
    last_name = request.POST.get('last_name')

    context = RequestContext(request)
    if request.method == 'POST':
        # ensure cleanup of any previous session
        request.session.flush()
        apicontext = backend.get_api_context(request=request)
        try:
            response = backend.api_signup(apicontext, email=email, password=password, first_name=first_name, last_name=last_name)
            request.session['curr_profile'] = response['profile']
            request.session['api_sessionid'] = response['sessionid']
            request.session.save()
            messages.success(request, 'Welcome to the Shared TO-DO app')
            return redirect(reverse('todo_lists'))
        except backend.ApiException, e:
            messages.error(request, e.message)
    context['email'] = email or ''
    context['first_name'] = first_name or ''
    context['last_name'] = last_name or ''
    return render(request, "signup.html", context_instance=context)


def signin(request):
    email = request.POST.get('email')
    password = request.POST.get('password')

    context = RequestContext(request)
    if request.method == 'POST':
        # ensure cleanup of any previous session
        request.session.flush()
        apicontext = backend.get_api_context(request=request)
        try:
            response = backend.api_signin(apicontext, email=email, password=password)
            request.session['curr_profile'] = response['profile']
            request.session['api_sessionid'] = response['sessionid']
            request.session.save()
            messages.success(request, 'Welcome back to the Shared TO-DO app')
            return redirect(reverse('todo_lists'))
        except backend.ApiException, e:
            messages.error(request, e.message)
    context['email'] = email or ''
    return render(request, "signin.html", context_instance=context)


def signout(request):
    apicontext = backend.get_api_context(request=request)
    request.session.flush()
    backend.api_signout(apicontext)
    return redirect(reverse('home'))


def profile(request):
    apicontext = backend.get_api_context(request=request)

    email = request.POST.get('email')
    password = request.POST.get('password')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')

    context = RequestContext(request)
    if request.method == 'POST':
        # ensure cleanup of any previous session
        try:
            response = backend.api_profile_update(apicontext, email=email, password=password, first_name=first_name, last_name=last_name)
            request.session['curr_profile'] = response['profile']
            messages.success(request, 'The changes were saved')
        except backend.ApiException, e:
            messages.error(request, e.message)

    context['email'] = email or ''
    context['first_name'] = first_name or ''
    context['last_name'] = last_name or ''

    response = backend.api_profile(apicontext)
    context.update(response['profile'])

    return render(request, "profile_update.html", context_instance=context)


def todo_lists(request):
    apicontext = backend.get_api_context(request=request)

    context = RequestContext(request)
    try:
        response = backend.api_todolist(apicontext)
        context['todolists'] = response['todolists']
    except backend.ApiException, e:
        messages.error(request, e.message)
        if e.code == 401:
            return redirect(reverse('signin'))
    return render(request, "todolist_list.html", context_instance=context)


def system_test(request):
    logging.debug('system_test(): sample: debug...')
    logging.info('system_test(): sample: info...')
    logging.warn('system_test(): sample: warning...')
    logging.error('system_test(): sample: error...')
    return render(request, "index.html")


def system_test_fatal(request):
    logging.info('system_test_fatal()')
    raise Exception('TESTING a 500 internal server error')
    return None
