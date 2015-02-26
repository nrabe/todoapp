"""
WSGI config for todoapp1 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "todoapp1.settings." + (os.environ.get("ENVIRONMENT") or "MUST-SET-ENVIRONMENT-VARIABLE-SEE-README"))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from whitenoise.django import DjangoWhiteNoise
application = DjangoWhiteNoise(application)

