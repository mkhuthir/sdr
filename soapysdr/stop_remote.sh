#!/usr/bin/sh

sudo systemctl stop soapyremote-server.service
sudo systemctl disable soapyremote-server.service
sudo systemctl status soapyremote-server.service

