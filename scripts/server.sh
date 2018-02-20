#!/usr/bin/env bash
ROOT_PATH=$(dirname $(dirname $0))
cd $ROOT_PATH

#waiting for db
./scripts/wait-for-it.sh db:3306

#create database if it is not there yet
python -c 'import pymysql; pymysql.connect(user="root", host="db").cursor().execute("create database if not exists adsrental CHARACTER SET utf8;")'

python manage.py collectstatic --noinput > /dev/nul

#install DB and fixtures
# python manage.py migrate adsrental
# python manage.py migrate
# python manage.py loaddata adsrental/fixtures/fixtures.json

# Start Gunicorn processes
echo Starting Gunicorn.
gunicorn -D config.wsgi:application -b 0.0.0.0:80 --reload
gunicorn config.wsgi:application \
  --bind 0.0.0.0:443 \
  --certfile=/app/cert/adsrental_com.crt \
  --keyfile=/app/cert/csr.key \
  --ca-certs=/app/cert/adsrental_com.ca-bundle \
  --worker-class gevent \
  --workers 13 \
  --timeout 3000 \
  --graceful-timeout 3000 \
  --worker-connections 10000 \
  --max-requests 10000 \
  --error-logfile=- \
  --reload
