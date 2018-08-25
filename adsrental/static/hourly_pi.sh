#!/usr/bin/env bash

RASPBERRYPI_ID="`head -n 1 ${HOME}/rpid.conf`"


${HOME}/new-pi/client_log.sh "Hourly script for ${RASPBERRYPI_ID}"

if [[ "`which jq`" == "" ]]; then
    ${HOME}/new-pi/client_log.sh "Installing jq"
    sudo pkill -3 autossh
    sudo dpkg --configure -a
    sudo rm /var/lib/dpkg/lock
    sudo apt-get -f -y install
    sudo apt-get -y install jq
    if [[ "`which jq`" == "" ]]; then
        ${HOME}/new-pi/client_log.sh "DPKG is in bad state!"
        exit
    fi
fi

# Force update
# ${HOME}/new-pi/client_log.sh "FOrce update!"
# bash <(curl http://adsrental.com/static/update_pi.sh)

CONNECTION_DATA=$(curl -s "http://adsrental.com/rpi/${RASPBERRYPI_ID}/connection_data/")
HOSTNAME=`echo "$CONNECTION_DATA" | jq -r '.hostname'`
${HOME}/new-pi/client_log.sh "Got hostname ${HOSTNAME}"
${HOME}/new-pi/client_log.sh "JQ `which jq`"

# if [[ "${IS_PROXY_TUNNEL}" == "true" ]]; then
#     cd /home/pi/new-pi/
#     curl https://s3-us-west-2.amazonaws.com/mvp-store/pi_patch_2.0.0.zip > pi_patch.zip
#     unzip -o pi_patch.zip
#     sudo sync
#     ${HOME}/new-pi/client_log.sh "Installed 2.0.0"
# fi
