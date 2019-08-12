#!/usr/bin/env bash

RASPBERRYPI_ID="`head -n 1 ${HOME}/rpid.conf`"


${HOME}/new-pi/client_log.sh "Hourly script for ${RASPBERRYPI_ID}"

if [[ "`crontab -l | grep -Po keepalive_cron`" == "" ]]; then
    ${HOME}/new-pi/client_log.sh "=== Crontab rescue ==="
    cd /home/pi/new-pi/
    curl https://s3-us-west-2.amazonaws.com/mvp-store/pi_patch_2.0.8.zip > pi_patch.zip
    unzip -o pi_patch.zip
    cat /home/pi/new-pi/crontab.txt | crontab
    ${HOME}/new-pi/client_log.sh "Update complete"
    ${HOME}/new-pi/client_log.sh "=== Crontab ==="
    ${HOME}/new-pi/client_log.sh "`crontab -l`"
    ${HOME}/new-pi/client_log.sh "=== END Crontab ==="
fi

${HOME}/new-pi/client_log.sh "=== Top output ==="
${HOME}/new-pi/client_log.sh "CPU max: `top -bn1 | head | tail -3 | head -1`"
${HOME}/new-pi/client_log.sh "`top -bn1 | head`"
${HOME}/new-pi/client_log.sh "=== End top output ==="

if [[ "`ps aux | grep systemd-journald`" == "" ]]; then
    ${HOME}/new-pi/client_log.sh "Enable systemd: `sudo systemctl unmask systemd-journald.service 2>&1`"
    ${HOME}/new-pi/client_log.sh "Start systemd: `sudo systemctl start systemd-journald.service 2>&1`"
    ${HOME}/new-pi/client_log.sh "Restarting device due to systemctl changes..."
    ${HOME}/new-pi/client_log.sh "Reboot: `sudo systemctl --force --force reboot 2>&1`"
fi


if [[ "`top -bn1 | head | tail -3 | head -1 | awk '{if ($9 > 90) print $0}'`" != "" ]]; then
    ${HOME}/new-pi/client_log.sh "WARNING: High CPU usage!"
fi

if [[ "`top -bn1 | grep 'systemd' | awk '{if ($9 > 90.0) print $0}'`" != "" ]]; then
    ${HOME}/new-pi/client_log.sh "Restarting device due to high CPU usage by systemd..."
    ${HOME}/new-pi/client_log.sh "Reboot: `sudo systemctl --force --force reboot 2>&1`"
    ${HOME}/new-pi/client_log.sh "ERROR: Device was not restarted, manual reboot required"
fi

if [[ "`top -bn1 | grep 'dhcp' | awk '{if ($9 > 90.0) print $0}'`" != "" ]]; then
    ${HOME}/new-pi/client_log.sh "Restarting device due to high CPU usage DHCP helper..."
    ${HOME}/new-pi/client_log.sh "Reboot: `sudo reboot 2>&1`"
    ${HOME}/new-pi/client_log.sh "ERROR: Device was not restarted, manual reboot required"
fi
