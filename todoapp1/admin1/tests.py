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
            logging.info('tests: testing admin %s', l)
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

    def test_admin_1_demo_grid(self):
        c = Client(enforce_csrf_checks=False)
        c.login(username=self.user_admin.username, password=self.user_admin_password)
        response = c.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)  # should redirect to login

        # get the template page
        print '--------------------------- PAGE'
        response = c.get(reverse('admin:backend1_handsontabledemo_changelist'))
        self.assertEqual(response.status_code, 200)  # should redirect to login
        # get the data
        print '--------------------------- DATA'
        response = c.post(reverse('admin:backend1_handsontabledemo_changelist'))
        self.assertEqual(response.status_code, 200)  # should redirect to login
        response = json.loads(response.content)
        for r in response['table_data']:
            print '*', r
        # add one record
        print '--------------------------- INCORRECT CREATE'
        request = {'changes': json.dumps([{'id': '_hOt__Id__1'}])}
        response = c.post(reverse('admin:backend1_handsontabledemo_changelist'), data=request)
        self.assertEqual(response.status_code, 200)  # should redirect to login
        response = json.loads(response.content)
        assert response.get('errors')
        for r in response.get('errors'):
            print 'EXPECTED.ERROR=', r
        # add one record
        print '--------------------------- INCORRECT UPDATE'
        request = {'changes': json.dumps([{'id': '1', 'test_integer': None}])}
        response = c.post(reverse('admin:backend1_handsontabledemo_changelist'), data=request)
        self.assertEqual(response.status_code, 200)  # should redirect to login
        response = json.loads(response.content)
        assert response.get('errors')
        for r in response.get('errors'):
            print 'EXPECTED.ERROR=', r
        print '---------------------------'

        print '--------------------------- CORRECT UPDATE'
        request = {'changes': json.dumps([{'id': 1,
                                           'test_foreign_key_null__L': "test5 test5 nrabe2+testusermass_5@gmail.com",
                                           'test_foreign_key_null': 15338,
                                           'test_int_choices': 2,
                                           'test_int_choices__L': 'two',
                                           'test_int_choices_null': 1,
                                           'test_int_choices_null__L': 'one',
                                           '_hOt_rowno': 1}])}
        response = c.post(reverse('admin:backend1_handsontabledemo_changelist'), data=request)
        self.assertEqual(response.status_code, 200)  # should redirect to login
        response = json.loads(response.content)
        assert not response.get('errors'), response
        for r in response['table_data']:
            if r['id'] == 1:
                assert r['test_int_choices'] == 2, r
                assert r['test_int_choices__L'] == 'two', r['test_int_choices__L']
                assert r['test_int_choices_null'] == 1, r
                assert r['test_int_choices_null__L'] == 'one', r['test_int_choices_null__L']
        print '---------------------------'

        print '--------------------------- AUTOCOMPLETE'
        request = {'query': ''}
        response = c.post(reverse('admin:backend1_handsontabledemo_autocomplete', args=['test_foreign_key']), data=request)
        self.assertEqual(response.status_code, 200)  # should redirect to login
        response = json.loads(response.content)
        assert response.get('items') and not response.get('errors'), response
        for r in response['items'][:3]:
            print 'AUTOCOMPLETE.ITEM =', r
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

