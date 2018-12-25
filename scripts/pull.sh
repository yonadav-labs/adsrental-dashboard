#!/usr/bin/env bash

CONFIG="docker-compose.prod.yml"


cd ~/dashboard/
git pull
docker-compose -f ${CONFIG} build

if [ "$1" = "migrate" ]; then
    docker-compose -f ${CONFIG} run web python manage.py migrate adsrental
fi

docker-compose -f ${CONFIG} up --remove-orphans -d
