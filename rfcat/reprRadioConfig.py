#!/usr/bin/python

from rflib import *

print("Connecting to RF dongle....")

d=RfCat()

print("Getting Radio Configuration....\n")
print(d.reprRadioConfig())
