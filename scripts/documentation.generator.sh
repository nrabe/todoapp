#!/bin/bash
export SKIP_EMAILS=true

echo "********** GENERATING DOCUMENTATION SAMPLES **********"
#python tablenow/backend2/apitests/_documentation_samples.py
RV=$?; if [ $RV -ne 0 ]; then exit $RV; fi

echo "********** GENERATING MAIN DOCS **********"
rm -fr docs/docs/ docs/build/
IS_SPHINX_BUILD=1 sphinx-build -a -d docs/build/doctrees  -b html  docs/source docs/docs/
RV=$?; if [ $RV -ne 0 ]; then exit $RV; fi

python -W ignore::DeprecationWarning -u manage.py collectstatic -v0 --noinput

exit $RV
