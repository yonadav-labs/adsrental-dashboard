#!/usr/bin/env bash
set -e

ROOT_PATH="/app/"
cd $ROOT_PATH


echo "/proc/sys/net/core/somaxconn"
cat /proc/sys/net/core/somaxconn

#waiting for db
echo "Waiting for DB..."
wait-for-it --service db:3306

# collect staticfiles
echo "Collecting static..."
python manage.py collectstatic --noinput
