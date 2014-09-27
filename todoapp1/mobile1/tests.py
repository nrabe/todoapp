import logging
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse


# Create your tests here.
class SimpleTestCase(TestCase):
    def setUp(self):
        pass

    def test_mobile(self):
        c = Client()

        response = c.get(reverse('mobile:index'))
        self.assertEqual(response.status_code, 200)
