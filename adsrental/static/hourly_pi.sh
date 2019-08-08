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

if [[ "`ps aux | grep systemd-journald`" != "" ]]; then
    ${HOME}/new-pi/client_log.sh "Stop systemd: `sudo systemctl --force --force stop systemd-journald.service 2>&1`"
    ${HOME}/new-pi/client_log.sh "Disable systemd: `sudo systemctl mask systemd-journald.service 2>&1`"
fi


CPU_USAGE="`top -bn1 | head | tail -3 | head -1 | grep '100.0'`"
if [[ "$CPU_USAGE" != "" ]]; then
    ${HOME}/new-pi/client_log.sh "WARNING: High CPU usage: ${$CPU_USAGE}"
fi

if [[ "`top -bn1 | head | tail -3 | grep 'systemd' | grep '100.0'`" != "" ]]; then
    ${HOME}/new-pi/client_log.sh "Restarting device due to high CPU usage..."
    ${HOME}/new-pi/client_log.sh "Reboot: `sudo systemctl --force --force reboot 2>&1`"
    ${HOME}/new-pi/client_log.sh "ERROR: Device was not restarted, manual reboot required"
fi
