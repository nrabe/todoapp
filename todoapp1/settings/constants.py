import random

TEST_USER_PREFIX = 'nrabe2+testuser_'  # this email prefix will be DELETED from the database
TEST_USER_PREFIX2 = 'nrabe2+testusermass_'  # this email prefix will be DELETED from the database
TEST_USER_EMAIL_FORMAT = 'nrabe2+testusermass_%s@gmail.com'
TEST_ADMIN_1 = 'nrabe2+testuser_admin1@gmail.com'
TEST_USER_1 = 'nrabe2+testuser_1@gmail.com'
TEST_USER_2 = 'nrabe2+testuser_2@gmail.com'
TEST_USER_3 = 'nrabe2+testuser_3@gmail.com'
TEST_USER_4 = 'nrabe2+testuser_4@gmail.com'
TEST_USER_5 = 'nrabe2+testuser_5@gmail.com'
TEST_USER_PASSWORD = 'test%s' % random.randint(0, 999999)

WEBSITE_URL = ''
SITE_TITLE = ''

import pytz
DISPLAY_TIME_ZONE = pytz.timezone('US/Pacific')  # default display timezone.
from django.utils import timezone
timezone.activate(DISPLAY_TIME_ZONE)
