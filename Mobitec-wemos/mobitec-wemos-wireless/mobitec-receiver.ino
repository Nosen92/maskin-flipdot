/*

Sketch to be used in tandem with the mobitec-sender sketch.
Receives data packet from mobitec-sender module. If successful,
receiver sends an ACK packet, and writes the data payload to
the sign via the MAX485 module. 

NOTE: Max packet size is 32 bytes because of the NRF 24L01 protocol.

*/

#include <SPI.h>
#include <RF24.h>

// Define the radio
RF24 radio(16, 15);  // CE, CSN pins

// Define the pipe address (must match the sender's address)
const uint64_t pipe = 0xE8E8F0F0E1LL;

void setup() {
  Serial.begin(4800);              // Expected bitrate by the sign
  radio.begin();
  radio.openReadingPipe(1, pipe);  // Open a reading pipe
  radio.setPALevel(RF24_PA_HIGH);  // Set power level
  radio.startListening();          // Start listening for incoming data
}

void loop() {
  uint8_t pipe;
  if (radio.available(&pipe)) {
    uint8_t bytes = radio.getPayloadSize();
    byte payload[bytes] = {};     // Adjust size if necessary
    radio.read(&payload, bytes);  // fetch payload from FIFO
    Serial.write(payload, bytes); // Writes data to the sign via the MAX485 module
  }

  /*
  PAYLOAD INSPECTION - INTERFERES WITH SIGN FUNCTION
  Serial.print("Recieved: ");
  for (int i = 0; i < sizeof(payload); i++) {
    Serial.write(payload[i]);
    Serial.print(".");
  }
  Serial.println("");
*/
}
