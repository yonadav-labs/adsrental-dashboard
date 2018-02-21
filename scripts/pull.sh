#!/usr/bin/env bash
cd ~/dashboard/
git pull


if [ "$1" = "restart" ]; then
    echo "restart"
    docker-compose -f docker-compose.dev.yml build
    docker-compose -f docker-compose.dev.yml run web python manage.py migrate adsrental
    docker-compose -f docker-compose.dev.yml up --remove-orphans -d
else
    docker exec dashboard_web_1 python manage.py collectstatic --noinput > /dev/null
fi

#docker-compose -f docker-compose.dev.yml run web python manage.py migrate
#docker-compose -f docker-compose.dev.yml run web python manage.py loaddata fixtures
