#!/usr/bin/python

from rflib import *

#-------------------------------------------------------------------------------
frequancy	= 315000000
modulation	= MOD_ASK_OOK
datarate	= 4800
#-------------------------------------------------------------------------------

d = RfCat()
d.setFreq(frequancy)
d.setMdmModulation(modulation)
d.setMdmDRate(datarate)

d.setMaxPower() # Maximum Power
d.lowball()	# Configures the radio to use the lowest level of filtering.
#-------------------------------------------------------------------------------

print "Starting Reception..."
d.RFlisten()

