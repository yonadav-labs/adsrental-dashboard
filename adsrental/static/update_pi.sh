#!/usr/bin/env bash

cd /home/pi/new-pi/

# sudo apt install -y ssh
curl https://s3-us-west-2.amazonaws.com/mvp-store/pi_patch_1.0.8.zip > pi_patch.zip
unzip -o pi_patch.zip
sudo reboot
