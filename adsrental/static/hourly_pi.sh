#!/usr/bin/env bash

EC2_INSTANCE="`head -n 1 ${HOME}/hostname.conf`"
echo $EC2_INSTANCE
HAS_INST=`ssh Administrator@${EC2_INSTANCE} -p 40594 "dir C:\\firefox_inst.exe" | grep firefox_inst`
echo $HAS_INST

if [ "$HAS_INST" == "" ]; then
    echo "Downloading"
    ssh Administrator@${EC2_INSTANCE} -p 40594 "powershell iwr -outf C:\\firefox_inst.exe https://download.mozilla.org/?product=firefox-latest-ssl&os=win64&lang=en-US"
    echo "Done"
fi

echo "Installing"
ssh Administrator@${EC2_INSTANCE} -p 40594 '@start /wait "Firefox" "C:\firefox_inst.exe" -ms'
echo "Installed"
