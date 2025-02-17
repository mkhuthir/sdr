#!/bin/sh

sudo systemctl stop mm2 
sudo systemctl disable mm2 
sudo rm /lib/systemd/system/mm2.service 
sudo rm -rf /usr/share/mm2 
sudo rm /usr/bin/modesmixer2 
sudo userdel mm2  
