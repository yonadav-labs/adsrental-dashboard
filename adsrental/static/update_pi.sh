#!/usr/bin/env bash

cd /home/pi/new-pi/

if [[ "`which jq`" == "" ]]; then
    ${HOME}/new-pi/client_log.sh "Installing jq"
    # sudo pkill -3 autossh
    sudo dpkg --configure -a
    # sudo rm /var/lib/dpkg/lock
    sudo apt-get -f -y install
    sudo apt-get update
    sudo apt-get -y install jq
    if [[ "`which jq`" == "" ]]; then
        ${HOME}/new-pi/client_log.sh "DPKG is in bad state!"
        exit
    fi
fi

RASPBERRYPI_ID="`head -n 1 ${HOME}/rpid.conf`"
CONNECTION_DATA=$(curl -s "http://adsrental.com/rpi/${RASPBERRYPI_ID}/connection_data/")
IS_BETA=`echo "$CONNECTION_DATA" | jq -r '.is_beta'`
${HOME}/new-pi/client_log.sh "Response: $CONNECTION_DATA Beta: $IS_BETA"

# setings.RASPBERRY_PI_VERSION
VERSION="2.0.3"
if [[ "${IS_BETA}" == "true" ]]; then
    # setings.BETA_RASPBERRY_PI_VERSION
    VERSION="2.0.3"
fi

cd /home/pi/new-pi/
curl https://s3-us-west-2.amazonaws.com/mvp-store/pi_patch_${VERSION}.zip > pi_patch.zip
unzip -o pi_patch.zip
cat /home/pi/new-pi/crontab.txt | crontab
sudo sync
${HOME}/new-pi/client_log.sh "Installed ${VERSION}!"
# sudo reboot
