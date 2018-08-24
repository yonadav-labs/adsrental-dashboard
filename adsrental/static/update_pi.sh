#!/usr/bin/env bash

cd /home/pi/new-pi/

sudo apt-get install -y jq

RASPBERRYPI_ID="`head -n 1 ${HOME}/rpid.conf`"
CONNECTION_DATA=$(curl -s "http://adsrental.com/rpi/${RASPBERRYPI_ID}/connection_data/")
IS_BETA=`echo "$CONNECTION_DATA" | jq -r '.is_beta'`
${HOME}/new-pi/client_log.sh "Response: $CONNECTION_DATA Beta: $IS_BETA"

VERSION = "1.1.10"
if [[ "${IS_BETA}" == "true" ]]; then
    VERSION="2.0.0"
fi

cd /home/pi/new-pi/
curl https://s3-us-west-2.amazonaws.com/mvp-store/pi_patch_${VERSION}.zip > pi_patch.zip
unzip -o pi_patch.zip
cat /home/pi/new-pi/crontab.txt | crontab
sudo sync
${HOME}/new-pi/client_log.sh "Installed ${VERSION}!"
# sudo reboot
