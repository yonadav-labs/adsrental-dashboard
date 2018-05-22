@echo off

if not "%1"=="am_admin" (powershell start -verb runas '%0' am_admin & exit)

if exist C:\Antidetect_7.3.1.zip (
    echo [!] Latest Antidetect is already downloaded. To download again, please delete C:\Antidetect_7.3.1.zip file
) else (
    echo [*] Downloading latest Antidetect
    powershell iwr -outf C:\Antidetect_7.3.1.zip https://s3-us-west-2.amazonaws.com/mvp-store/Antidetect_7.3.1.zip
)

echo [*] Installing Antidetect
if exist C:\Antidetect\antidetect.conf (
    echo [*] Creating backup of existing config
    powershell Copy-Item C:\Antidetect\antidetect.conf -Destination C:\antidetect.conf.backup
)
powershell Expand-Archive -force C:\Antidetect_7.3.1.zip -DestinationPath C:\
if exist C:\antidetect.conf.backup (
    echo [*] Applying config backup
    powershell Copy-Item C:\antidetect.conf.backup -Destination C:\Antidetect\antidetect.conf
)

echo [*] Adding shortcuts to desktop
powershell iwr https://adsrental.com/static/antidetect/browser.exe -outf C:\Users\Administrator\Desktop\Browser.exe
powershell Copy-Item C:/Antidetect/variables.conf -Destination C:\Users\Administrator\Desktop\variables.conf

echo [*] Done. You can close this window now and use Browser.exe from desktop

pause
