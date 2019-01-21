#!/usr/bin/env bash
ROOT_PATH=$(dirname $(dirname $0))
cd $ROOT_PATH

#waiting for db
# ./scripts/wait-for-it.sh db:3306

#create database if it is not there yet
#python -c 'import pymysql; pymysql.connect(user="root", host="db").cursor().execute("create database if not exists adsrental;")'

# python manage.py collectstatic --noinput

#install DB and fixtures
# python manage.py makemigrations adsrental
# python manage.py migrate adsrental
# python manage.py migrate
# python manage.py loaddata adsrental/fixtures/fixtures.json

sysctl -w net.core.somaxconn=65535
/usr/bin/supervisord
