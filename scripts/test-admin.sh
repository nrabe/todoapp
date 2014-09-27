#!/bin/sh


DIR="$( cd "$( dirname $( dirname "${BASH_SOURCE[0]}" ))" && pwd )"
cd $DIR

source venv/bin/activate

echo "##### TESTING admin1"
python -W ignore::DeprecationWarning manage.py test todoapp1.admin1 --failfast --settings="todoapp1.settings.tests_settings"
RV=$?; if [ $RV -ne 0 ]; then exit $RV; fi

exit $RV
