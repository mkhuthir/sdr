#!/bin/sh

echo "Listening to AIS Long Range (156.775MHz and 156.825MHz)"
rtl_ais -l 156.775M -r 156.825M -n
