#!/usr/bin/env bash
OUTPUT=`curl -s -o /dev/null -w "%{http_code}" http://adsrental.com:9999`
DATE=`date '+%Y-%m-%d %H:%M:%S'`

echo "${DATE} Status: ${OUTPUT}"

if ! [ "$OUTPUT" = "200" ]; then
    echo "${DATE} Restarting..."
    cd ~/dashboard/
    docker-compose -f docker-compose.prod.yml restart rdpclient
fi
