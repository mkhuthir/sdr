#ifndef CC2530_H_
#define CC2530_H_

#include <compiler.h>

SBIT(P0_0, 0x80, 0);
SBIT(P1_1, 0x90, 1);

SFR(P0SEL, 0xF3);
SFR(P1SEL, 0xF4);
SFR(P0DIR, 0xFD);
SFR(P1DIR, 0xFE);

#endif
