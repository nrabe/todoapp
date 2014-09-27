import os
import logging

# Import the configuration settings file
settings_module = "todoapp1.settings." + (os.environ.get("ENVIRONMENT") or "MUST-SET-ENVIRONMENT-VARIABLE-SEE-README")
print "Django version 1.7, using settings '%s'" % settings_module

config_module = __import__(settings_module, globals(), locals(), 'todoapp1')
for setting in dir(config_module):
    if setting == setting.upper():
        locals()[setting] = getattr(config_module, setting)

TEST_RUNNER = 'todoapp1.settings.tests_common.NoDbTestRunner'
IS_RUNNING_TEST = True  # utility flag, to skip certain operations (sending an email, for example) while running tests

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
