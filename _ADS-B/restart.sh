  GNU nano 7.2                                           restart.sh                                                     
#!/bin/sh

sudo service dump1090-fa stop
sudo service ais-catcher stop

rtl_biast -d 0 -b 0
rtl_biast -d 1 -b 1

sudo service dump1090-fa start
sudo service ais-catcher start

sudo service piaware restart
sudo service rbfeeder restart
sudo service adsbexchange-feed restart
sudo service adsbexchange-mlat restart
sudo service adsbexchange-stats restart
sudo service pfclient restart

sudo service ais-catcher-control restart
sudo service sxfeeder restart

