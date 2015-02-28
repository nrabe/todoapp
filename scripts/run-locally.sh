#!/bin/sh

python -W ignore::DeprecationWarning -u manage.py collectstatic -v0 --noinput
python -W ignore::DeprecationWarning -u manage.py runserver 0.0.0.0:8600
