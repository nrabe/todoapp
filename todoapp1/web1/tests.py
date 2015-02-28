# -*- coding: utf-8 -*-
import logging
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse

from todoapp1.settings import constants
from todoapp1.backend1 import api as backend


# Create your tests here.
class SimpleTestCase(TestCase):
    def setUp(self):
        apicontext = backend.get_api_context()
        backend.api_sys_create_test_data(apicontext)
        pass

    def test_basic_webpages(self):
        c = Client()

        response = c.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

        response = c.get(reverse('signin'))
        self.assertEqual(response.status_code, 200)

        response = c.post(reverse('signin'), {'email': constants.TEST_USER_1, 'password': constants.TEST_USER_PASSWORD})
        self.assertRedirects(response, reverse('todo_lists'), 302, 200)

        response = c.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

        response = c.post(reverse('profile'), {'first_name': 'test+1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The changes were saved')

        response = c.get(reverse('todo_lists'))
        self.assertEqual(response.status_code, 200)

    def test_error_handling(self):
        c = Client()

        response = c.get(reverse('system_test'))
        self.assertEqual(response.status_code, 200)

        response = c.get('sys/test/404-page-not-found/')
        self.assertEqual(response.status_code, 404)

        try:
            response = c.get(reverse('system_test_fatal'))
            self.assertEqual(response.status_code, 500)
        except Exception, e:
            self.assert_('TESTING a 500 internal server error' in repr(e), 'expected a programming error')
