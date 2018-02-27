#!/usr/bin/env bash

EC2_INSTANCE="`head -n 1 ${HOME}/hostname.conf`"
HAS_INST=`ssh Administrator@${EC2_INSTANCE} -p 40594 "dir C:\\firefox_inst.exe" | grep firefox_inst`

if [ "$HAS_INST" == "" ]; then
    ssh Administrator@${EC2_INSTANCE} -p 40594 "powershell iwr -outf C:\\firefox_inst.exe https://download.mozilla.org/?product=firefox-latest-ssl&os=win64&lang=en-US"
fi

ssh Administrator@${EC2_INSTANCE} -p 40594 '@start /wait "Firefox" "C:\firefox_inst.exe" -ms'
