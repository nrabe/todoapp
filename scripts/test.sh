#!/bin/sh


DIR="$( cd "$( dirname $( dirname "${BASH_SOURCE[0]}" ))" && pwd )"
cd $DIR

source venv/bin/activate

echo "##### TESTING backend1"
python -W ignore::DeprecationWarning manage.py test todoapp1.backend1 --failfast --settings="todoapp1.settings.tests_settings"
RV=$?; if [ $RV -ne 0 ]; then exit $RV; fi

echo "##### TESTING admin1"
scripts/test-admin.sh
RV=$?; if [ $RV -ne 0 ]; then exit $RV; fi

echo "##### TESTING web1"
python -W ignore::DeprecationWarning manage.py test todoapp1.web1 --failfast --settings="todoapp1.settings.tests_settings"
RV=$?; if [ $RV -ne 0 ]; then exit $RV; fi

echo "##### TESTING mobile1"
python -W ignore::DeprecationWarning manage.py test todoapp1.mobile1 --failfast --settings="todoapp1.settings.tests_settings"
RV=$?; if [ $RV -ne 0 ]; then exit $RV; fi

exit $RV
