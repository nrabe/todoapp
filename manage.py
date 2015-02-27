#!/usr/bin/env python
import os
import sys
import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "todoapp1.settings." + os.environ.get("ENVIRONMENT", "MUST-SET-ENVIRONMENT-VARIABLE-SEE-README"))
logging.warn("(manage.py) DJANGO_SETTINGS_MODULE=%s %r", os.environ.get("DJANGO_SETTINGS_MODULE"), sys.argv)

if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
