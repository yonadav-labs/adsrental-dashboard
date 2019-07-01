#!/usr/bin/env bash
ROOT_PATH=$(dirname $(dirname $0))
cd $ROOT_PATH

# ENV=test python manage.py migrate adsrental
# ENV=test python manage.py migrate
ENV=test python manage.py loaddata adsrental/fixtures/test.json
# ENV=test python manage.py runserver_plus & > /dev/null
ENV=test python manage.py behave --use-existing-database --keepdb --stop --no-skipped $@
