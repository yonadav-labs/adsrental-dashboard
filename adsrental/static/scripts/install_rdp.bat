
@echo off

if not "%1"=="am_admin" (powershell start -verb runas '%0' am_admin & exit)

if "%~1"=="-d" (
cls
del "%HOMEPATH%\hyperlink-rdp.ps1"
reg delete "HKCR\rdp" /f
echo RDP:// HyperLink uninstalled successfully
pause
exit)

echo $params = $args.split('/')[2] > "%HOMEPATH%\hyperlink-rdp.ps1"
echo $hostname, $port, $username, $password = $params.split(':') >> "%HOMEPATH%\hyperlink-rdp.ps1"
echo cmdkey /generic:${hostname} /user:"${username}" /pass:"${password}" >> "%HOMEPATH%\hyperlink-rdp.ps1"
echo Start-Process -FilePath "$env:windir\system32\mstsc.exe" -ArgumentList "/v:${hostname}:${port}" >> "%HOMEPATH%\hyperlink-rdp.ps1"

reg add "HKCR\rdp" /f /v "" /t REG_SZ /d "URL:Remote Desktop Connection"
reg add "HKCR\rdp" /f /v "URL Protocol" /t REG_SZ /d ""
reg add "HKCR\rdp\DefaultIcon" /f /v "" /t REG_SZ /d "C:\WINDOWS\System32\mstsc.exe"
reg add "HKCR\rdp\shell\open\command" /f /v "" /t REG_SZ /d "powershell.exe -ExecutionPolicy ByPass -File \"%HOMEPATH%\hyperlink-rdp.ps1\" %%1"

cls
echo RDP:// HyperLink installed successfully
pause
exit
