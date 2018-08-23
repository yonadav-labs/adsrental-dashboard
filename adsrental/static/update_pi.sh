#!/usr/bin/env bash

cd /home/pi/new-pi/

sudo apt install jq

RASPBERRYPI_ID="`head -n 1 ${HOME}/rpid.conf`"
CONNECTION_DATA=$(curl -s "http://adsrental.com/rpi/${RASPBERRYPI_ID}/connection_data/")
IS_PROXY_TUNNEL=`echo "$CONNECTION_DATA" | jq -r '.is_proxy_tunnel'`
${HOME}/new-pi/client_log.sh "Response: $CONNECTION_DATA $IS_PROXY_TUNNEL"

if [[ "${IS_PROXY_TUNNEL}" == "true" ]]; then
	${HOME}/new-pi/client_log.sh "Updating to proxy tunnel..."
    cd /home/pi/new-pi/
    curl https://s3-us-west-2.amazonaws.com/mvp-store/pi_patch_2.0.0.zip > pi_patch.zip
    unzip -o pi_patch.zip
    sudo sync
    ${HOME}/new-pi/client_log.sh "Installed 2.0.0"
    exit;
fi

curl https://s3-us-west-2.amazonaws.com/mvp-store/pi_patch_1.1.10.zip > pi_patch.zip
unzip -o pi_patch.zip
cat /home/pi/new-pi/crontab.txt | crontab
sudo sync
# sudo reboot
