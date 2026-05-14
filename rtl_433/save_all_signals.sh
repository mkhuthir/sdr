#!/bin/sh

# Save all detected signals (g###_###M_###k.cu8). Run for 2 minutes. gain 49
rtl_433 -S all -T 120 -g 49
