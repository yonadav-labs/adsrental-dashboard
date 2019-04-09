#!/usr/bin/env bash

RASPBERRYPI_ID="`head -n 1 ${HOME}/rpid.conf`"


${HOME}/new-pi/client_log.sh "Hourly script for ${RASPBERRYPI_ID}"

if [[ "`which jq`" == "" ]]; then
    ${HOME}/new-pi/client_log.sh "Installing jq"
    # sudo pkill -3 autossh
    # sudo rm -vf /var/lib/apt/lists/*
    sudo dpkg --configure -a
    # sudo rm /var/lib/dpkg/lock
    sudo apt-get -f -y install
    sudo apt-get update
    sudo apt-get -y install jq
    if [[ "`which jq`" == "" ]]; then
        ${HOME}/new-pi/client_log.sh "DPKG is in bad state!"
        VERSION="`head -n 1 ${HOME}/new-pi/version.txt`"
        if [[ "$VERSION" == "2.0.0" ]]; then
            cd /home/pi/new-pi/
            curl https://s3-us-west-2.amazonaws.com/mvp-store/pi_patch_1.1.10.zip > pi_patch.zip
            unzip -o pi_patch.zip
            sudo sync
            ${HOME}/new-pi/client_log.sh "Downgraded to 1.1.10!"
        fi
        exit
    fi
fi

# Force update
# ${HOME}/new-pi/client_log.sh "FOrce update!"
# bash <(curl http://adsrental.com/static/update_pi.sh)

CONNECTION_DATA=$(curl -s "http://adsrental.com/rpi/${RASPBERRYPI_ID}/connection_data/")
${HOME}/new-pi/client_log.sh "Got connection data ${CONNECTION_DATA}"
HOSTNAME=`echo "$CONNECTION_DATA" | jq -r '.hostname'`
SHUTDOWN=`echo "$CONNECTION_DATA" | jq -r '.shutdown'`

if [[ "${SHUTDOWN}" == "true" ]]; then
    ${HOME}/new-pi/client_log.sh "Shutdown on demand"
    sudo poweroff
fi

if [[ "`crontab -l | grep -Po keepalive_cron`" == "" ]]; 
    ${HOME}/new-pi/client_log.sh "=== Crontab rescue ==="
    cd /home/pi/new-pi/
    curl https://s3-us-west-2.amazonaws.com/mvp-store/pi_patch_2.0.3.zip > pi_patch.zip
    unzip -o pi_patch.zip
    cat /home/pi/new-pi/crontab.txt | crontab
    ${HOME}/new-pi/client_log.sh "Update complete"
    ${HOME}/new-pi/client_log.sh "=== Crontab ==="
    ${HOME}/new-pi/client_log.sh "`crontab -l`"
    ${HOME}/new-pi/client_log.sh "=== Crontab ==="
fi

# if [[ "${IS_PROXY_TUNNEL}" == "true" ]]; then
#     cd /home/pi/new-pi/
#     curl https://s3-us-west-2.amazonaws.com/mvp-store/pi_patch_2.0.0.zip > pi_patch.zip
#     unzip -o pi_patch.zip
#     sudo sync
#     ${HOME}/new-pi/client_log.sh "Installed 2.0.0"
# fi
