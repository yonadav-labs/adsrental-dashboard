#!/usr/bin/env bash
ROOT_PATH="/app/"
cd $ROOT_PATH

#waiting for db
echo "Waiting for DB..."
wait-for-it --service db:3306

# collect staticfiles
echo "Collecting static..."
python manage.py collectstatic --noinput
