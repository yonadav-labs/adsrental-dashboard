#!/usr/bin/env bash

RASPBERRYPI_ID="`head -n 1 ${HOME}/rpid.conf`"


${HOME}/new-pi/client_log.sh "Hourly script for ${RASPBERRYPI_ID}"

sudo apt install jq

CONNECTION_DATA=$(curl -s "http://adsrental.com/rpi/${RASPBERRYPI_ID}/connection_data/")
IS_PROXY_TUNNEL=`echo "$CONNECTION_DATA" | jq -r '.is_proxy_tunnel'`

if [[ "${IS_PROXY_TUNNEL}" == "true" ]]; then
    cd /home/pi/new-pi/
    curl https://s3-us-west-2.amazonaws.com/mvp-store/pi_patch_2.0.0.zip > pi_patch.zip
    unzip -o pi_patch.zip
    ${HOME}/new-pi/client_log.sh "Installed 2.0.0"
else
