from todoapp1.settings.common import *  # @UnusedWildImport

DEBUG = False
TEMPLATE_DEBUG = True

# in DEV, enable the authentication middleware
BASIC_WWW_AUTHENTICATION = True
if BASIC_WWW_AUTHENTICATION:
    MIDDLEWARE_CLASSES += ('todoapp1.middleware.BasicAuthenticationMiddleware',)
