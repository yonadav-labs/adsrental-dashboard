#!/usr/bin/env bash
ROOT_PATH=$(dirname $(dirname $0))
cd $ROOT_PATH

#waiting for db
./scripts/wait-for-it.sh db:3306

#create database if it is not there yet
#python -c 'import pymysql; pymysql.connect(user="root", host="db").cursor().execute("create database if not exists adsrental;")'

python manage.py collectstatic --noinput > /dev/null

#install DB and fixtures
# python manage.py makemigrations adsrental
# python manage.py migrate adsrental
# python manage.py migrate
# python manage.py loaddata adsrental/fixtures/fixtures.json


while true; do
    echo "Re-starting Gunicorn runserver"
    gunicorn -D config.wsgi_debug:application \
      --bind 0.0.0.0:80 \
      --worker-class=eventlet \
      --error-logfile=/app/app_log/error_http.log \
      --access-logfile=/app/app_log/access_http.log \
      --reload
    gunicorn config.wsgi_debug:application \
        --bind 0.0.0.0:443 \
        --certfile=/app/cert/adsrental_com.crt \
        --keyfile=/app/cert/csr.key \
        --ca-certs=/app/cert/adsrental_com.ca-bundle \
        --worker-class=eventlet \
        --workers 4 \
        --timeout 300 \
        --graceful-timeout 300 \
        --worker-connections 100000 \
        --max-requests 100000 \
        --error-logfile=- \
        --access-logfile=- \
        --reload
    sleep 5
done
