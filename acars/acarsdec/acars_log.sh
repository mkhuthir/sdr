#!/bin/sh

echo "Writing decoded messages to $(date +"%Y_%m_%d_%I_%M_%p").log"
acarsdec \
	-o2 \
	-l $(date +"%Y_%m_%d_%I_%M_%p").log \
	-r 0 131.475 131.525 131.725 131.825

