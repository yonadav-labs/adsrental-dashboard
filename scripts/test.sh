#!/usr/bin/env bash
ROOT_PATH=$(dirname $(dirname $0))
cd $ROOT_PATH

ENV=test python manage.py loaddata adsrental/fixtures/test.json
ENV=test python manage.py runserver_plus &
ENV=test python manage.py test -v 2
