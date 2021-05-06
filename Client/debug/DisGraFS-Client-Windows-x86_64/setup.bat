@echo off

reg query HKEY_CLASSES_ROOT\Installer\Dependencies\WinFsp>nul 2>nul
if %errorlevel%==0 echo WinFsp Already Installed && goto WINFSPINSTALLED

echo Installing WinFsp...
winfsp-1.8.20304.msi
echo WinFsp Installed

:WINFSPINSTALLED

echo Installing python module watchdog
pip install watchdog
echo Complete

echo Installing python module websockets
pip install websockets
echo Complete

echo Generating .reg file...
echo Windows Registry Editor Version 5.00>DisGraFS-Client-Register-Generated.reg
echo [HKEY_CLASSES_ROOT\disgrafs]>>DisGraFS-Client-Register-Generated.reg
echo @="URL:disgrafs Protocol Handler">>DisGraFS-Client-Register-Generated.reg
echo "URL Protocol"="">>DisGraFS-Client-Register-Generated.reg
echo [HKEY_CLASSES_ROOT\disgrafs\shell]>>DisGraFS-Client-Register-Generated.reg
echo [HKEY_CLASSES_ROOT\disgrafs\shell\open]>>DisGraFS-Client-Register-Generated.reg
echo [HKEY_CLASSES_ROOT\disgrafs\shell\open\command]>>DisGraFS-Client-Register-Generated.reg
set cwd=%~dp0
set cwdDoubleBackslash=%cwd:\=\\%
echo @="cmd.exe /C cd /d %cwdDoubleBackslash%&&python DisGraFS-Client.py \"%%1\"">>DisGraFS-Client-Register-Generated.reg
echo Complete

echo Please allow regedit to modify your registry
DisGraFS-Client-Register-Generated.reg
echo Complete

echo Installation Complete
echo Please note that whenever this directory is moved, setup.bat should be re-run
pause
