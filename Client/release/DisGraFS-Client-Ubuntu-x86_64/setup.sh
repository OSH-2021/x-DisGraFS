#!/bin/sh

echo Installing python module watchdog
pip3 install watchdog
echo Complete

echo Installing python module websockets
pip3 install websockets
echo Complete

echo Generating .desktop file...
echo [Desktop Entry]>./disgrafs.desktop
echo Type=Application>>./disgrafs.desktop
echo Exec=/usr/bin/python3 $(dirname $(readlink -f "$0"))/DisGraFS-Client.py %u>>./disgrafs.desktop
echo Name=disgrafs>>./disgrafs.desktop
echo GenericName=DisGraFS Client URL Protocol Handler>>./disgrafs.desktop
echo Terminal=true>>./disgrafs.desktop
echo Categories=Network\;Application\;>>./disgrafs.desktop
echo MimeType=x-scheme-handler/disgrafs>>./disgrafs.desktop
echo Encoding=UTF-8>>./disgrafs.desktop
echo Complete

echo Please allow me to add disgrafs.desktop to your desktop database
sudo cp ./disgrafs.desktop /usr/share/applications/disgrafs.desktop
sudo update-desktop-database
echo Complete

echo Installation Complete
echo Please note that whenever this directory is moved, setup.sh should be re-run
