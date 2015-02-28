from todoapp1.settings.common import *  # @UnusedWildImport

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
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

os.environ.setdefault('SENTRY_DSN', 'https://ffdc9132abe44bd9850c62f748162c77:f4b46cc652b34b8a992d7fa29ce4ba86@app.getsentry.com/38770')

GRAPHENEDB_URL = "http://localhost:7474/db/data/"

# in DEV, enable the authentication middleware
BASIC_WWW_AUTHENTICATION = False
if BASIC_WWW_AUTHENTICATION:
    MIDDLEWARE_CLASSES += ('todoapp1.middleware.BasicAuthenticationMiddleware',)
