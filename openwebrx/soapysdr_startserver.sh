#!/usr/bin/sh

sudo systemctl stop openwebrx
sudo systemctl enable soapyremote-server.service
sudo systemctl start soapyremote-server.service
sudo systemctl status soapyremote-server.service

