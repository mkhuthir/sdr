// Feather M0 RFM9x TX
// -*- mode: C++ -*-

// Example sketch showing how to create a simple messaging client (transmitter)
// with the RH_RF95 class. RH_RF95 class does not provide for addressing or
// reliability, so you should only use RH_RF95 if you do not need the higher
// level messaging abilities.


#include <SPI.h>
#include <RH_RF95.h>

/* Wiring for Feather M0 with built in RFM9x
#define RFM95_CS  8
#define RFM95_RST 4
#define RFM95_INT 3
*/
// Wiring for FeatherWing on Feather M0 
#define RFM95_CS  10 // "B"
#define RFM95_RST 11 // "A"
#define RFM95_INT 6  // "D"

// Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, Power +13dbM
// RFM_FREQ is centre Frequency in MHz. 137.0 to 1020.0
// RFM95/96/97/98 comes in several different frequency ranges, 
// and setting a frequency outside that range of your radio will probably not work

#define RFM95_FREQ    434.0
#define RFM95_TXPOWER 5

// Message

#define msg "123456789012345678901234567890123456789"

char radiopacket[sizeof(msg)] = msg;
  
// Singleton instance of the radio driver
RH_RF95 rf95(RFM95_CS, RFM95_INT);

void setup() 
{
  pinMode(RFM95_RST, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);
  
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  // sending will start only when serial is connected.
  Serial.begin(115200);
  while (!Serial) {
    delay(1);
  }

  delay(100);

  Serial.println("Feather M0 RFM9x TX Test!");

  // ******************** manual reset radio ********************
  digitalWrite(LED_BUILTIN, HIGH);
  
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);

  // ******************** initilize radio ********************
  while (!rf95.init()) {
    Serial.println("RFM9x radio init failed");
    Serial.println("Uncomment '#define SERIAL_DEBUG' in RH_RF95.cpp for detailed debug info");
    while (1);
  }

  Serial.println("RFM9x radio init OK!");

  // ******************** set parameters ********************
  if (!rf95.setFrequency(RFM95_FREQ)) {
    Serial.println("setFrequency failed");
    while (1);
  }
  Serial.print("Set Freq to: "); Serial.println(RFM95_FREQ);
  
  rf95.setTxPower(RFM95_TXPOWER, false);
  Serial.print("Set TX Power to: "); Serial.println(RFM95_TXPOWER);

  digitalWrite(LED_BUILTIN, LOW);
}


void loop()
{

  Serial.println("Ready to Send..."); 
  while (Serial.available() < 1);
  Serial.read();

  Serial.print("\nSending: "); 
  Serial.println(radiopacket);
  digitalWrite(LED_BUILTIN, HIGH);
  rf95.send((uint8_t *)radiopacket, sizeof(msg));

  Serial.println("Waiting for packet to complete..."); 
  rf95.waitPacketSent();
  digitalWrite(LED_BUILTIN, LOW);
  Serial.println("Packet completed.");
  

}
