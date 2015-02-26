#!/bin/sh

DIR="$( cd "$( dirname $( dirname "${BASH_SOURCE[0]}" ))" && pwd )"
cd $DIR

source venv/bin/activate

read -r -p "Are you sure? all the information will be lost [y/N]" response
case $response in
    [yY][eE][sS]|[yY])
        mv db.sqlite3 /tmp/
        
        ./manage.py makemigrations
        RV=$?; if [ $RV -ne 0 ]; then exit $RV; fi
        ./manage.py migrate
        RV=$?; if [ $RV -ne 0 ]; then exit $RV; fi
        echo "from django.contrib.auth.models import User; User.objects.create_superuser('nrabe2+a@gmail.com', 'nrabe2+a@gmail.com', 'admin')" | ./manage.py shell
        RV=$?; if [ $RV -ne 0 ]; then exit $RV; fi
        python -W ignore::DeprecationWarning todoapp1/backend1/tools/generate_random_data.py
        RV=$?; if [ $RV -ne 0 ]; then exit $RV; fi
        ;;
esac

