from todoapp1.settings.common import *  # @UnusedWildImport

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True
COMPRESS_ENABLED = False
SKIP_EMAILS = True

#LOGGING['loggers']['django.db']['level'] = 'DEBUG'  # enable/disable SQL logging

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
os.environ['MEMCACHEIFY_USE_LOCAL'] = 'True'
CACHES = memcacheify()

# os.environ.setdefault('DATABASE_URL', 'postgres://USERNAME@localhost/DATABASE')
# DATABASES = postgresify()
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
}


GRAPHENEDB_URL = "http://localhost:7474/db/data/"

# in DEV, enable the authentication middleware
BASIC_WWW_AUTHENTICATION = False
if BASIC_WWW_AUTHENTICATION:
    MIDDLEWARE_CLASSES += ('todoapp1.web1.middleware.BasicAuthenticationMiddleware',)
