#!/bin/sh

DIR="$( cd "$( dirname $( dirname "${BASH_SOURCE[0]}" ))" && pwd )"
cd $DIR

source venv/bin/activate

export ENVIRONMENT=${ENVIRONMENT:-nahuel}
python manage.py permission
