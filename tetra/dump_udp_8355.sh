#!/usr/bin/sh

nc -l -u -p 8355 | tetra-rx /dev/stdin
