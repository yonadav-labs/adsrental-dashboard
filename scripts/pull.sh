#!/usr/bin/env bash


if [ "$1" = "migrate" ]; then
    cd ~/migrate/dashboard/
    git pull
    docker-compose -f docker-compose.dev.yml build
    docker-compose -f docker-compose.dev.yml run web python manage.py migrate adsrental
    cd ~/dashboard/
    docker-compose -f docker-compose.dev.yml build
    docker-compose -f docker-compose.dev.yml up --remove-orphans -d
    exit
fi
if [ "$1" = "restart" ]; then
    echo "restart"
    cd ~/dashboard/
    git pull
    docker-compose -f docker-compose.dev.yml build
    docker-compose -f docker-compose.dev.yml up --remove-orphans -d
    exit
fi

cd ~/dashboard/
git pull
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up --remove-orphans -d

#docker-compose -f docker-compose.dev.yml run web python manage.py migrate
#docker-compose -f docker-compose.dev.yml run web python manage.py loaddata fixtures
