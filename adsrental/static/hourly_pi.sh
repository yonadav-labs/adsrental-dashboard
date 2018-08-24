#!/usr/bin/env bash

RASPBERRYPI_ID="`head -n 1 ${HOME}/rpid.conf`"


${HOME}/new-pi/client_log.sh "Hourly script for ${RASPBERRYPI_ID}"

sudo apt-get install -y jq

CONNECTION_DATA=$(curl -s "http://adsrental.com/rpi/${RASPBERRYPI_ID}/connection_data/")
HOSTNAME=`echo "$CONNECTION_DATA" | jq -r '.hostname'`
${HOME}/new-pi/client_log.sh "Got hostname ${HOSTNAME}"

# if [[ "${IS_PROXY_TUNNEL}" == "true" ]]; then
#     cd /home/pi/new-pi/
#     curl https://s3-us-west-2.amazonaws.com/mvp-store/pi_patch_2.0.0.zip > pi_patch.zip
#     unzip -o pi_patch.zip
#     sudo sync
#     ${HOME}/new-pi/client_log.sh "Installed 2.0.0"
# fi
