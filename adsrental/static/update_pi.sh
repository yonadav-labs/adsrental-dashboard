#!/usr/bin/env bash

cd /home/pi/new-pi/

# sudo apt install -y ssh libffi-dev python-pip openssl libssl-dev
# sudo pip install -U pip
# sudo pip install paramiko requests
curl https://s3-us-west-2.amazonaws.com/mvp-store/pi_patch_1.0.25.zip > pi_patch.zip
unzip -o pi_patch.zip

# ./install.sh
cat /home/pi/new-pi/crontab.txt | crontab
sudo reboot
