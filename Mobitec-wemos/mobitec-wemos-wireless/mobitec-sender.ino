/*

Sketch to be used in tandem with the mobitec-receiver sketch.
DIY hardcoding of the mobitec package, but checksum is automatic 
(albeit not fully implemented).

Package is then transmitted via NRF 24L01 to the receiver 
every 3 seconds. If transmission is successful, it prints
OK to the serial monitor.

NOTE: Max packet size is 32 bytes because of the NRF 24L01 protocol.

*/

#include <SPI.h>
#include <RF24.h>

// Define the radio
RF24 radio(16, 15);  // CE, CSN pins

// Define the pipe address (must match the receiver's address)
const uint64_t pipe = 0xE8E8F0F0E1LL;

// Payload to send
byte packet[] = {
  0xff,
  0x06,
  0xa2,
  0xd0,  // Resolution
  0x70,
  0xd1,
  0x10,
  0xd2,  // Offset
  0x06,
  0xd3,
  0x11,
  0xd4,  // Font
  0x65,
  0x48,  // H
  0x45,  // E
  0x4c,  // L
  0x4c,  // L
  0x4f,  // O
  0x20,
  0x57,  // W
  0X4F,  // O
  0X52,  // R
  0X4C,  // L
  0X44,  // D
  0xe0,  // Checksum placeholder, will be calculated in setup()
  0xff   // Stop byte
};

int length = sizeof(packet);

// Checksum8 Modulo 256, 0xff's are compensated for since they should not be included
byte calculateChecksum(byte byteArray[], int length) {
  unsigned int sum = 0;
  for (int i = 0; i < length; i++) {
    sum += byteArray[i];
  }
  sum += 2;  // Compensate for the two 0xff's
  byte checksum = sum % 256;
  return checksum;  // Return checksum as byte (mod 256)
}

void setup() {

  byte checksum = calculateChecksum(packet, length);

/* // Needs rewrite, broken (however tbf literally 1/128 odds to run into this tho)
  if (checksum == 0xff) {
    packet[length - 2] = 0xfe;
    packet[length - 1] = 0x01;
  } else {
    packet[length - 2] = checksum;
  }
*/

  packet[length - 2] = checksum; // Replace placeholder with real checksum

  Serial.begin(9600);
  radio.begin();
  radio.openWritingPipe(pipe);     // Set the pipe address for sending
  radio.setPALevel(RF24_PA_HIGH);  // Set power level
  radio.stopListening();           // Stop listening, we are sending data
}

void loop() {
  bool success = radio.writeBlocking(packet, sizeof(packet), 500);
  if (success) {
    Serial.println("OK");
  } else {
    Serial.println("Fail");
  }
  delay(3000);  // Send the payload every 3 seconds, chosen arbitrarily honestly
}
