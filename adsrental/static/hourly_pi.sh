#!/usr/bin/env bash

EC2_INSTANCE="`head -n 1 ${HOME}/hostname.conf`"

if [[ "$EC2_INSTANCE" == *html* ]]; then
    ${HOME}/new-pi/client_log.sh "Getting config"
    bash ${HOME}/new-pi/main.sh
fi


${HOME}/new-pi/client_log.sh "Hourly script for ${EC2_INSTANCE}"

# ssh Administrator@${EC2_INSTANCE} -p 40594 "Taskkill /IM ruby.exe /F"
# ssh Administrator@${EC2_INSTANCE} -p 40594 "powershell Rename-Item -Path C:\\Users\\Administrator\\Desktop\\auto -newName C:\\Users\\Administrator\\Desktop\\auto_backup"
# ssh Administrator@${EC2_INSTANCE} -p 40594 'del "C:\Users\Administrator\Desktop\Restart Tunnel.url"'
# ssh Administrator@${EC2_INSTANCE} -p 40594 'del "C:\Users\Administrator\Desktop\Firefox.lnk"'
# ssh Administrator@${EC2_INSTANCE} -p 40594 'del "C:\Users\Public\Desktop\Firefox.lnk"'
ssh Administrator@${EC2_INSTANCE} -p 40594 "C:\\Antidetect\\vc_redist.x86.exe /q"


DIR_OUTPUT=`ssh Administrator@${EC2_INSTANCE} -p 40594 'dir C:\\Users\\Administrator\\firefox_wp.png' | grep png`
if [ "$DIR_OUTPUT" == "" ]; then
    ssh Administrator@${EC2_INSTANCE} -p 40594 'powershell iwr https://adsrental.com/static/images/firefox_wp.png -OutFile C:\\Users\\Administrator\\firefox_wp.png'
    ssh Administrator@${EC2_INSTANCE} -p 40594 'powershell iwr https://adsrental.com/static/images/Firefox.lnk -OutFile C:\\Users\\Administrator\\Desktop\\FireFox.lnk'
fi
# ssh Administrator@${EC2_INSTANCE} -p 40594 'del C:\Users\Administrator\Desktop\Browser.exe'
# ssh Administrator@${EC2_INSTANCE} -p 40594 'del C:\Users\Public\Desktop\Browser.exe'
# ssh Administrator@${EC2_INSTANCE} -p 40594 'del C:\Users\Public\Desktop\Firefox.lnk'
# ssh Administrator@${EC2_INSTANCE} -p 40594 'reg add "HKEY_CURRENT_USER\Control Panel\Desktop" /v Wallpaper /t REG_SZ /d C:\Users\Administrator\firefox_wp.png /f'
# ssh Administrator@${EC2_INSTANCE} -p 40594 'RUNDLL32.EXE user32.dll,UpdatePerUserSystemParameters'


TASKLIST_OUTPUT=`ssh Administrator@${EC2_INSTANCE} -p 40594 'tasklist'`
TASKLIST_FIREFOX=`echo "$TASKLIST_OUTPUT" | grep 'firefox.exe'`
if ! [ "$TASKLIST_FIREFOX" == "" ]; then
    NETSTAT_OUTPUT=`ssh Administrator@${EC2_INSTANCE} -p 40594 'netstat -an'`
    RDP_NETSTAT=`echo "$NETSTAT_OUTPUT" | grep 'TCP' | grep 'ESTABLISHED' | grep ':23255'`
    if [ "$RDP_NETSTAT" == "" ]; then
        ssh Administrator@${EC2_INSTANCE} -p 40594 "taskkill /IM firefox.exe /F"
        ssh Administrator@${EC2_INSTANCE} -p 40594 "taskkill /IM FirefoxPortable.exe /F"
    fi
fi