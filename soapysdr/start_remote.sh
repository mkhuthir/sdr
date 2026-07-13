#!/usr/bin/sh

sudo systemctl enable soapyremote-server.service
sudo systemctl start soapyremote-server.service
sudo systemctl status soapyremote-server.service

