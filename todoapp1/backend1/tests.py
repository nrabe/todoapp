# -*- coding: utf-8 -*-
import json
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from django.conf import settings

from todoapp1.backend1 import api as backend


class SimpleTestCase(TestCase):
    """ each test method will run in the normal DB (no extra DB will be created), but in a separate transaction and rolled back after the method's end """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_basics(self):
        c = Client()

        response = c.get(reverse('api:api_sys_test', kwargs={'x_client_version': 'UNITTEST.0.0.1'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        try:
            response = c.get(reverse('api:api_sys_test', kwargs={'x_client_version': 'UNITTEST.0.0.1'}) + '?test=fatal_error')
            assert False, 'Expecting an error'
        except ZeroDivisionError:
            pass

        # test single jsonrpc call
        JSONRPC_ENDPOINT = reverse('api:jsonrpc', kwargs={'x_client_version': 'UNITTEST.0.0.1'})
        request = {"jsonrpc": "2.0", "method": "api_sys_test", "params": {}, "id": "aaa"}
        response = c.post(JSONRPC_ENDPOINT, content_type='application/json', data=json.dumps(request))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        response = json.loads(response.content)
        assert not response.get('error') and response.get('result'), response

        # test bach jsonrpc calls
        requests = [
            {"jsonrpc": "2.0", "method": "api_sys_test", "params": {}, "id": 0},
            {"jsonrpc": "2.0", "method": "api_sys_test", "params": {"test": "fatal_error"}, "id": 1},
            {"jsonrpc": "2.0", "method": "api_sys_test", "params": {"test": "error"}, "id": 2},
            {"jsonrpc": "2.0", "method": "api_config", "id": 3},
        ]
        responses = c.post(JSONRPC_ENDPOINT, content_type='application/json', data=json.dumps(requests), headers={'X-CLIENT-VERSION': 'unittest.0.0.0'})
        self.assertEqual(responses.status_code, 200)
        self.assertEqual(responses['Content-Type'], 'application/json')
        responses = json.loads(responses.content)
        response_id_0 = [x for x in responses if x['id'] == 0][0]
        response_id_1 = [x for x in responses if x['id'] == 1][0]
        response_id_2 = [x for x in responses if x['id'] == 2][0]
        response_id_3 = [x for x in responses if x['id'] == 3][0]
        assert not response_id_0.get('error') and response_id_0.get('result'), response_id_0
        assert response_id_1.get('error') and not response_id_1.get('result'), response_id_1
        assert response_id_2.get('error') and not response_id_2.get('result'), response_id_2
        assert not response_id_3.get('error') and response_id_3.get('result'), response_id_3

        # test the native version
        apicontext = backend.get_api_context()
        response = backend.api_sys_test(apicontext)
        try:
            response = backend.api_sys_test(apicontext, test='fatal_error')
            assert False, 'Expecting an error'
        except ZeroDivisionError:
            pass

    def test_todo_ops(self):

        apicontext1 = backend.get_api_context()
        backend.api_signup(apicontext1, email=settings.TEST_USER_1, password='test', first_name='test1', last_name='test1')

        response = backend.api_todolist_set(apicontext1, title="test1")
        todolist1 = response['todolist']

        response = backend.api_todolist(apicontext1, todolist_id=todolist1.id)
        todolists = [x for x in response['todolists'] if x.id == todolist1.id]
        assert len(todolists) == 1 and todolists[0].id == todolist1.id

        response = backend.api_todolist(apicontext1)
        todolists = [x for x in response['todolists'] if x.id == todolist1.id]
        assert len(todolists) == 1 and todolists[0].id == todolist1.id

        response = backend.api_todolist_item_set(apicontext1, todolist_id=todolist1.id, text="test1")

        #
        # now another user tries to access it, change it or share it and fails
        #
        apicontext2 = backend.get_api_context()
        backend.api_signup(apicontext2, email=settings.TEST_USER_2, password='test', first_name='test1', last_name='test1')

        try:
            response = backend.api_todolist(apicontext2, todolist_id=todolist1.id)
        except backend.ApiException, e:
            assert e.code == 500, e

        try:
            response = backend.api_todolist_set(apicontext2, todolist_id=todolist1.id, title='test+2')
        except backend.ApiException, e:
            assert e.code == 500, e

        try:
            response = backend.api_todolist_share(apicontext2, todolist_id=todolist1.id, share_with_email=settings.TEST_USER_2)
        except backend.ApiException, e:
            assert e.code == 500, e

        #
        # now user1 shares the list with user2
        #
        response = backend.api_todolist_share(apicontext1, todolist_id=todolist1.id, share_with_email=settings.TEST_USER_2)

        # even after sharing it, the to-do cannot be changed
        try:
            response = backend.api_todolist_set(apicontext2, todolist_id=todolist1.id, title='test+2')
        except backend.ApiException, e:
            assert e.code == 500, e

        # and now user2 can add items to the list
        response = backend.api_todolist_item_set(apicontext2, todolist_id=todolist1.id, text="test2 (from user2)")

        # user2 can also  see it direct or in his list
        response = backend.api_todolist(apicontext2, todolist_id=todolist1.id)
        todolists = [x for x in response['todolists'] if x.id == todolist1.id]
        assert len(todolists) == 1 and todolists[0].id == todolist1.id

        response = backend.api_todolist(apicontext2)
        todolists = [x for x in response['todolists'] if x.id == todolist1.id]
        assert len(todolists) == 1 and todolists[0].id == todolist1.id

    def test_signin_signup_profile(self):

        apicontext = backend.get_api_context()

        response = backend.api_signup(apicontext, email=settings.TEST_USER_1, password='test', first_name='testuser1', last_name='testuser1')
        assert response.get('profile'), response
        response = backend.api_signin(apicontext, email=settings.TEST_USER_1, password='test')
        assert response.get('profile'), response

        backend.api_profile(apicontext)
        assert response.get('profile') and response['profile']['first_name'] == 'testuser1' and \
            response['profile']['last_name'] == 'testuser1', response

        response = backend.api_profile_update(apicontext, first_name='testuser1+1', last_name='testuser1+1')
        assert response.get('profile') and response['profile']['first_name'] == 'testuser1+1' and \
            response['profile']['last_name'] == 'testuser1+1', response

        backend.api_signout(apicontext)
