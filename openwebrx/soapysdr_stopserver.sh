#!/usr/bin/sh

sudo systemctl stop soapyremote-server.service
sudo systemctl disable soapyremote-server.service

sudo systemctl start openwebrx
sudo systemctl status openwebrx
