#include <Arduino.h>
// Tested with wemos d1 mini
// Connected wemos tx to max485 di

byte packet[] = {
//0xff,  // Starting byte, sent separately below to not include in checksum
  0x0b,  // Sign address
  0xa2,  // Always a2
  0xd0,  // Display width
  0x70,  // 112px
  0xd1,  // Display height
  0x10,  // 0px
  0xd2,  // Horizontal offset
  0x00,  // 0px right
  0xd3,  // Vertical offset
  0x00,  // 0px down
  0xD4,  // Font
  0x60,  // 13px font
  0x45,  // E
  0x58,  // X
  0x41,  // A
  0x4d,  // M
  0x50,  // P
  0x4c,  // L
  0x45,  // E
//0xcd,  // Checksum
//0xff   // Stop byte
};

int length = sizeof(packet) / sizeof(packet[0]);


void setup() {

  pinMode(LED_BUILTIN, OUTPUT);    // Diagnose with LED if needed
  digitalWrite(LED_BUILTIN, HIGH); // LED off when HIGH!

  // initialize serial port:
  Serial.begin(4800);
  
  while (!Serial) {
    ; // wait for serial port to connect.
  }

  delay(3000); // Makes communication much more robust (maybe d1 mini boot process garbles to the sign, and it takes a while for the sign to timeout and clear its serial buffer?)

  Serial.write(0xff);
  Serial.write(packet, length);
  byte checksum = calculateChecksum(packet, length);
  if (checksum == 0xff) { Serial.write(0xfe); Serial.write(0x01); }
  else if (checksum == 0xfe) { Serial.write(0xfe); Serial.write(0x00); }
  else { Serial.write(checksum); }  
  Serial.write(0xff);


}

void loop() {
  digitalWrite(LED_BUILTIN, LOW);
  delay(1000);
  digitalWrite(LED_BUILTIN, HIGH);
  delay(1000);
}

byte calculateChecksum(byte byteArray[], int length) {
  unsigned int sum = 0;
  
  for (int i = 0; i < length; i++) {
    sum += byteArray[i];
  }
  
  return (byte)(sum % 256);  // Return checksum as byte (mod 256)
}
