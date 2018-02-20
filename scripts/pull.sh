#!/usr/bin/env bash
cd ~/dashboard/
git pull

docker-compose -f docker-compose.dev.yml build

if [ "$1" = "restart" ]; then
    echo "restart"
    docker-compose -f docker-compose.dev.yml run web python manage.py migrate adsrental
    docker-compose -f docker-compose.dev.yml up --remove-orphans -d
fi

#docker-compose -f docker-compose.dev.yml run web python manage.py migrate
#docker-compose -f docker-compose.dev.yml run web python manage.py loaddata fixtures
