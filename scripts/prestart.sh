#!/usr/bin/env bash
ROOT_PATH="/app/"
cd $ROOT_PATH

#waiting for db
echo "Waiting for DB..."
./scripts/wait-for-it.sh db:3306

# collect staticfiles
echo "Collecting static..."
python manage.py collectstatic --noinput
