#!/usr/bin/python

from rflib import * 

#-------------------------------------------------------------------------------
frequancy	= 315000000
modulation	= MOD_ASK_OOK
datarate	= 4800
msg 		= "\x84\xe7\x08\x42\x10\x84\xe7\x38\x00\x00\x00\x00\x00\x00"*10
#-------------------------------------------------------------------------------

d = RfCat()
d.setFreq(frequancy)
d.setMdmModulation(modulation)
d.setMdmDRate(datarate)

#-------------------------------------------------------------------------------

print "Starting Transmission..."
d.RFxmit(msg)
print 'Transmission Complete'
