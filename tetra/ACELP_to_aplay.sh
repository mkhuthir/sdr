#!/usr/bin/sh

cat ~/Downloads/out/*.out | cdecoder /dev/stdin /dev/stdout | sdecoder /dev/stdin /dev/stdout | aplay -f S16_LE -r 8000 -c 1
