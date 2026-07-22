#!/usr/bin/sh

nc -l -u -p 8355 > ~/Downloads/$(date +"%Y%m%d_%H%M%S_raw.bits")
