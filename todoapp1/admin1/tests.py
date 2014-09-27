# -*- coding: utf-8 -*-
import re
import logging
import json
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

import todoapp1.settings.common_constants as constants


# Create your tests here.
class SimpleTestCase(TestCase):
    def setUp(self):
        self.user_admin = User.objects.create_superuser(constants.TEST_ADMIN_1, constants.TEST_ADMIN_1, 'test')
        self.user_admin.save()
        self.user_admin_password = 'test'

    def tearDown(self):
        self.user_admin.delete()
        pass

    def test_admin_pages_automatic(self):
        c = Client(enforce_csrf_checks=False)
        c.login(username=self.user_admin.username, password=self.user_admin_password)

        response = c.get('/admin/', follow=True)
        self.assertContains(response, '/admin/logout/', msg_prefix='#0')

        links = re.findall(' href="([^"]+)"', response.content, re.S | re.M)
        for l in sorted(list(set(links))):
            if l.endswith('.css') or l.endswith('.ico') or l.endswith('.png'):
                continue
            if l == '#':
                continue
            if 'logout' in l:
                continue
            logging.debug('tests: testing admin %s', l)
            response = c.get(l)
            self.assertEqual(response.status_code, 200, msg=l)
            self.assertContains(response, '/admin/logout/', msg_prefix=l)

    def test_admin_signin(self):
        c = Client(enforce_csrf_checks=False)
        response = c.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)  # should redirect to login

        c.login(username=self.user_admin.username, password=self.user_admin_password)
        response = c.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)  # should redirect to login

    def test_admin_z_demo_grid(self):
        c = Client(enforce_csrf_checks=False)
        c.login(username=self.user_admin.username, password=self.user_admin_password)
        response = c.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)  # should redirect to login

        # get the template page
        response = c.get(reverse('handsontable_demo'))
        self.assertEqual(response.status_code, 200)  # should redirect to login

        # get the data
        response = c.post(reverse('handsontable_demo'))
        self.assertEqual(response.status_code, 200)  # should redirect to login
        response = json.loads(response.content)
        print '---------------------------'
        for r in response['table_data']:
            print '*', r
        print '---------------------------'

        # add one record
        print '--------------------------- ADDING REC'
        request = {'changes': json.dumps([{'id': '_hOt__Id__1'}])}
        response = c.post(reverse('handsontable_demo'), data=request)
        self.assertEqual(response.status_code, 200)  # should redirect to login
        response = json.loads(response.content)
        if response.get('errors'):
            print 'RESP.ERROR', response['errors']
        else:
            for r in response['table_data']:
                print '*', r
        print '---------------------------'

#     def test_admin_pages(self):
#         c = Client()
#         c.login(username=self.user_admin.username, password=self.user_admin_password)
#
#         response = c.get(reverse('admin:backend1_moodtype_changelist'))
#         self.assertEqual(response.status_code, 200)  # should redirect to login
#
#         response = c.get(reverse('admin:backend1_place_changelist'))
#         self.assertEqual(response.status_code, 200)  # should redirect to login
#
#         response = c.get(reverse('admin:backend1_mood_changelist'))
#         self.assertEqual(response.status_code, 200)  # should redirect to login

