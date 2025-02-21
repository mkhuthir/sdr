#!/bin/sh

sudo service dump1090-fa stop
rtl_biast -b 1
sudo service dump1090-fa start

sudo service piaware restart
sudo service rbfeeder restart
sudo service adsbexchange-feed restart
sudo service adsbexchange-mlat restart
sudo service adsbexchange-stats restart
sudo service pfclient restart
