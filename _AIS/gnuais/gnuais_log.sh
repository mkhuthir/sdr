#!/bin/sh

echo "Writing decoded messages to $(date +"%Y_%m_%d_%I_%M_%p").log"
gnuais -o none >"$(date +"%Y_%m_%d_%I_%M_%p").log"
