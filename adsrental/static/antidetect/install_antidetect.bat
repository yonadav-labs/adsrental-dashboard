@echo off

if not "%1"=="am_admin" (powershell start -verb runas '%0' am_admin & exit)

if exist C:\Antidetect_7.3.1.zip (
    echo "[!] Latest Antidetect is already downloaded. TO download again, please delete C:\Antidetect_7.3.1.zip file"
) else (
    echo "[*] Downloading latest Antidetect"
    powershell iwr -outf C:\Antidetect_7.3.1.zip https://s3-us-west-2.amazonaws.com/mvp-store/Antidetect_7.3.1.zip
)

if exist C:\Antidetect (
    echo "[!] Antidetect is already installed. Delete C:\Antidetect to reinstall"
    echo "[!] This will also regenerate antidetect config"

) else (
    echo "[*] Installing Antidetect"
    powershell Expand-Archive -force C:\Antidetect_7.3.1.zip -DestinationPath C:\
)

echo "[*] Adding shortcuts to desktop"

powershell iwr https://adsrental.com/static/antidetect/browser.exe -outf C:\Users\Administrator\Desktop\Browser.exe
powershell Copy-Item C:/Antidetect/variables.conf -Destination C:\Users\Administrator\Desktop\variables.conf

echo "[*] Done. You can close this window now and use Browser.exe from desktop"

pause
