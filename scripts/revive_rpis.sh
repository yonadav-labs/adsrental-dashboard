#!/usr/bin/env bash
docker-compose -f /root/dashboard/docker-compose.dev.yml run web python manage.py revive_rpis
