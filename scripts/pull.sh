#!/usr/bin/env bash

CONFIG="docker-compose.prod.yml"

if [ "$1" = "migrate" ]; then
    cd ~/migrate/dashboard/
    git pull
    docker-compose -f ${CONFIG} build
    docker-compose -f ${CONFIG} run web python manage.py migrate adsrental
fi

cd ~/dashboard/
git pull
docker-compose -f ${CONFIG} build
docker-compose -f ${CONFIG} up --remove-orphans -d
