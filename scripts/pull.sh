#!/usr/bin/env bash

cd ~/dashboard/
git pull

docker-compose build

#docker-compose -f docker-compose.dev.yml run web python manage.py migrate
#docker-compose -f docker-compose.dev.yml run web python manage.py loaddata fixtures
docker-compose -f docker-compose.dev.yml up -d
