#!/bin/sh

echo "Writing decoded messages to $(date +"%Y_%m_%d_%I_%M_%p").log"
rtl_ais -n  2> "$(date +"%Y_%m_%d_%I_%M_%p").log"
