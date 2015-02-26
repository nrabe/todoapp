#!/bin/sh

python -W ignore::DeprecationWarning -u manage.py collectstatic -c --noinput
python -W ignore::DeprecationWarning -u manage.py runserver 0.0.0.0:8600
