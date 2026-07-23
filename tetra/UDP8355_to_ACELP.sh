#!/usr/bin/sh

nc -l -u -p 8355 | tetra-rx -d ~/Downloads/out
