#!/usr/bin/env bash
ROOT_PATH=$(dirname $(dirname $0))
cd $ROOT_PATH

#waiting for db
./scripts/wait-for-it.sh db:3306

#create database if it is not there yet
python -c 'import pymysql; pymysql.connect(user="root", host="db").cursor().execute("create database if not exists adsrental CHARACTER SET utf8;")'

python manage.py collectstatic --noinput

#install DB and fixtures
# python manage.py migrate adsrental
# python manage.py migrate
# python manage.py loaddata adsrental/fixtures/fixtures.json

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn config.wsgi:application \
    --worker-class gevent \
    --bind 0.0.0.0:8007 \
    --workers 3 \
    --timeout 3000 \
    --error-logfile=-

