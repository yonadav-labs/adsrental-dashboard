#!/usr/bin/env bash
cd ~/dashboard/
git pull

if [ "$1" = "migrate" ]; then
    docker-compose -f docker-compose.dev.yml build
    docker-compose -f docker-compose.dev.yml run web python manage.py migrate adsrental
    docker-compose -f docker-compose.dev.yml up --remove-orphans -d
    exit
fi
if [ "$1" = "restart" ]; then
    echo "restart"
    docker-compose -f docker-compose.dev.yml build
    docker-compose -f docker-compose.dev.yml up --remove-orphans -d
    exit
fi

# docker-compose -f docker-compose.dev.yml run web python manage.py collectstatic --noinput > /dev/null

#docker-compose -f docker-compose.dev.yml run web python manage.py migrate
#docker-compose -f docker-compose.dev.yml run web python manage.py loaddata fixtures
