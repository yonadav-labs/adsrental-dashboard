#!/usr/bin/env bash

EC2_INSTANCE="`head -n 1 ${HOME}/hostname.conf`"

if [[ "$EC2_INSTANCE" == *html* ]]; then
    ${HOME}/new-pi/client_log.sh "Getting config"
    bash ${HOME}/new-pi/main.sh
fi


${HOME}/new-pi/client_log.sh "Hourly script for ${EC2_INSTANCE}"

HAS_FF="`ssh Administrator@${EC2_INSTANCE} -p 40594 'dir C:\\Users\\Public\\Desktop\\Firefox.lnk' | grep Firefox.lnk`"
if [ "$HAS_FF" == "" ]; then
    ${HOME}/new-pi/client_log.sh "Firefox is not installed..."
    HAS_FF_INST="`ssh Administrator@${EC2_INSTANCE} -p 40594 'dir C:\\firefox_inst.exe' | grep firefox_inst`"
    if [ "$HAS_FF_INST" == "" ]; then
        ${HOME}/new-pi/client_log.sh "Firefox is not downloaded..."
        ssh Administrator@${EC2_INSTANCE} -p 40594 "powershell iwr -outf C:\\firefox_inst.exe https://download.mozilla.org/?product=firefox-latest-ssl&os=win64&lang=en-US"
    fi
    ssh Administrator@${EC2_INSTANCE} -p 40594 '@start /wait "Firefox" "C:\firefox_inst.exe" -ms'
    HAS_FF="`ssh Administrator@${EC2_INSTANCE} -p 40594 'dir C:\\Users\\Public\\Desktop\\Firefox.lnk' | grep Firefox.lnk`"
    if [ "$HAS_FF" == "" ]; then
        ${HOME}/new-pi/client_log.sh "Firefox is still missing..."
    else
        ${HOME}/new-pi/client_log.sh "Firefox is installed"
    fi
else
    ${HOME}/new-pi/client_log.sh "Firefox is already installed"
fi

HAS_ANTIDETECT="`ssh Administrator@${EC2_INSTANCE} -p 40594 'dir C:\\Antidetect\\antidetect.exe' | grep antidetect.exe`"
if [ "$HAS_ANTIDETECT" == "" ]; then
    ${HOME}/new-pi/client_log.sh "Antidetect is not installed..."
    HAS_ANTIDETECT_INST="`ssh Administrator@${EC2_INSTANCE} -p 40594 'dir C:\\Antidetect.zip' | grep Antidetect.zip`"
    if [ "$HAS_ANTIDETECT_INST" == "" ]; then
        ${HOME}/new-pi/client_log.sh "Antidetect is not downloaded..."
        ssh Administrator@${EC2_INSTANCE} -p 40594 "powershell iwr -outf C:\\Antidetect.zip https://s3-us-west-2.amazonaws.com/mvp-store/Antidetect.zip"
    fi
    ssh Administrator@${EC2_INSTANCE} -p 40594 "powershell Expand-Archive -force c:\\Antidetect.zip -DestinationPath c:\\"
    ssh Administrator@${EC2_INSTANCE} -p 40594 "powershell Copy-Item -Path 'C:\\Antidetect\\Browser.exe' -Destination C:\\Users\\Public\\Desktop\\"
    ssh Administrator@${EC2_INSTANCE} -p 40594 "powershell Copy-Item -Path 'C:\\Antidetect\\variables.conf' -Destination C:\\Users\\Public\\Desktop\\"
    ssh Administrator@${EC2_INSTANCE} -p 40594 "C:\\Antidetect\\vc_redist.x86.exe /q"
    ${HOME}/new-pi/client_log.sh "Antidetect is installed"
else
    ${HOME}/new-pi/client_log.sh "Antidetect is already installed"
fi

ssh Administrator@${EC2_INSTANCE} -p 40594 "Taskkill /IM ruby.exe /F"
ssh Administrator@${EC2_INSTANCE} -p 40594 "powershell Rename-Item -Path C:\\Users\\Administrator\\Desktop\\auto -newName C:\\Users\\Administrator\\Desktop\\auto_backup"
ssh Administrator@${EC2_INSTANCE} -p 40594 'del "C:\Users\Administrator\Desktop\Restart Tunnel.url"'
