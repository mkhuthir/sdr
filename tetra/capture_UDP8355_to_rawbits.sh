#!/usr/bin/sh

nc -l -u -p 8355 > $(date +"%Y%m%d_%H%M%S_raw.bits")
