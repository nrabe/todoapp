#!/bin/sh

DIR="$( cd "$( dirname $( dirname "${BASH_SOURCE[0]}" ))" && pwd )"
cd $DIR

source venv/bin/activate

python -W ignore::DeprecationWarning -u manage.py collectstatic --noinput
python -W ignore::DeprecationWarning -u manage.py runserver 8600
