#!/usr/bin/env bash
cd ~/dashboard/
git pull

docker-compose -f docker-compose.dev.yml build

if [ "$1" = "migrate" ]; then
    echo "migrate"
    docker-compose -f docker-compose.dev.yml run web python manage.py migrate adsrental
fi

#docker-compose -f docker-compose.dev.yml run web python manage.py migrate
#docker-compose -f docker-compose.dev.yml run web python manage.py loaddata fixtures
docker-compose -f docker-compose.dev.yml up --scale web=2 -d
