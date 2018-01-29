#!/usr/bin/env bash

cd /home/pi/new-pi/
sudo apt update
sudo apt upgrade
curl https://adsrental.com/static/new_pi.zip > new_pi.zip
unzip -o new_pi.zip
sudo reboot
