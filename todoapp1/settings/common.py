"""
Django settings for recommendation_project project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

sys.path.append(os.path.join(BASE_DIR))

from memcacheify import memcacheify
from postgresify import postgresify


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^ebl3u^!mpw-qqs22keczpw_#kxv1lg-i+(^ze&9#eed8g4)3s'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEMPLATE_DEBUG = False
IS_RUNNING_TEST = False  # utility flag, to skip certain operations (sending an email, for example) while running tests
SKIP_EMAILS = False  # when running locally, we may want to skip sending email messages
USE_API_LOGGING = True

# If True, all task will be executed right before sending the response (so, no async at all).
# Easier to set-up this way.
USE_TASK_QUEUE = False

# basic auth config for the website
BASIC_WWW_AUTHENTICATION_USERNAME = "biz"
BASIC_WWW_AUTHENTICATION_PASSWORD = "t8"
BASIC_WWW_AUTHENTICATION = False


ALLOWED_HOSTS = ['*']

# code to get Heroku Sendgrid integration
SENDGRID_USERNAME = os.environ.get('SENDGRID_USERNAME')
SENDGRID_PASSWORD = os.environ.get('SENDGRID_PASSWORD')

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = SENDGRID_USERNAME
EMAIL_HOST_PASSWORD = SENDGRID_PASSWORD
EMAIL_PORT = 587
EMAIL_USE_TLS = True
SKIP_EMAILS = False

SITE_ID = 1

# Application definition

INSTALLED_APPS = (
    'todoapp1.web1',
    'todoapp1.backend1',
    'todoapp1.backend_res1',
    'todoapp1.mobile1',
    'todoapp1.admin1',
    'pq',  # simple task queue ( django-pq )
    'django_admin_bootstrapped.bootstrap3',
    'django_admin_bootstrapped',
    'compressor',
    'django_markdown',
    'markdown',
    'django.contrib.flatpages',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

MIDDLEWARE_CLASSES = (
    'log_request_id.middleware.RequestIDMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'todoapp1.middleware.GlobalRequestMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'todoapp1.urls'

WSGI_APPLICATION = 'todoapp1.wsgi.application'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

STATIC_ROOT = os.path.normpath(os.path.join(BASE_DIR, 'static'))

# to serve the documentation in heroku DEV (and locally)
STATICFILES_DIRS = (
    os.path.abspath(os.path.join(BASE_DIR, 'docs/')),
)

MEDIA_ROOT = os.path.normpath(os.path.join(BASE_DIR, 'media'))
MEDIA_URL = "/media/"

TEMPLATE_LOADERS = (
                    'django.template.loaders.filesystem.Loader',
                    'todoapp1.web1.django_utils.Loader',
                    'django.template.loaders.app_directories.Loader',
                    )

TEMPLATE_CONTEXT_PROCESSORS = (
                                "django.contrib.auth.context_processors.auth",
                                "django.core.context_processors.debug",
                                "django.core.context_processors.i18n",
                                "django.core.context_processors.media",
                                "django.core.context_processors.static",
                                "django.core.context_processors.tz",
                                "django.contrib.messages.context_processors.messages",
                                "django.core.context_processors.request"
                                )

########## COMPRESSION CONFIGURATION
# See: http://django_compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_ENABLED
COMPRESS_ENABLED = True

COMPRESS_OFFLINE = True

# See: http://django-compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_CSS_HASHING_METHOD
COMPRESS_CSS_HASHING_METHOD = 'content'

# See: http://django_compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_CSS_FILTERS
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.template.TemplateFilter',
]

# See: http://django_compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_JS_FILTERS
COMPRESS_JS_FILTERS = [
    'compressor.filters.template.TemplateFilter',
]

COMPRESS_ENABLED = True
COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter']
COMPRESS_JS_FILTERS = []

########## END COMPRESSION CONFIGURATION

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = postgresify()
CACHES = memcacheify()

GRAPHENEDB_URL = os.environ.get("GRAPHENEDB_URL")

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'US/Pacific'  # this is the timezone for processing, storing dates... DISPLAY_TIME_ZONE should be used to convert it when rendering.
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'request_id': {
            '()': 'log_request_id.filters.RequestIDFilter'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'console': {
            "level": "DEBUG",
            'filters': ['request_id'],
            "class": "todoapp1.settings.colorlogging.RainbowLoggingHandler",
            'stream': sys.stderr
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'requests.packages.urllib3.connectionpool': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'ERROR',
        },
        'management_commands': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'mail_admins'],
            'propagate': False,
            'level': 'ERROR',
        },
        'django.db': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'INFO',
        },
    }
}

from common_constants import *  # @UnusedWildImport ... important for other parts of the system.
