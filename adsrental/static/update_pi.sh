#!/usr/bin/env bash

cd /home/pi/new-pi/

curl https://s3-us-west-2.amazonaws.com/mvp-store/pi_patch_1.1.8.zip > pi_patch.zip
unzip -o pi_patch.zip
cat /home/pi/new-pi/crontab.txt | crontab
sudo sync
# sudo reboot
