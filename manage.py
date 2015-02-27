#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "todoapp1.settings." + (os.environ.get("ENVIRONMENT") or "MUST-SET-ENVIRONMENT-VARIABLE-SEE-README"))
    print "(manage.py) DJANGO_SETTINGS_MODULE=", os.environ.get("DJANGO_SETTINGS_MODULE")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
