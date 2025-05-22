#include <Arduino.h>
#include <SPI.h>
#include <RF24.h>

RF24 radio(16, 15);  // CE, CSN
const uint64_t pipe = 0xE8E8F0F0E1LL;

const size_t MAX_PACKETS = 20;
const size_t CHUNK_SIZE = 30;
const size_t MAX_SIZE = MAX_PACKETS * CHUNK_SIZE;

byte receivedData[MAX_SIZE] = {0};
bool receivedFlags[MAX_PACKETS] = {false};

int totalPackets = -1;
int totalReceived = 0;
size_t messageLength = 0;

void setup() {
  Serial.begin(4800);
  radio.begin();
  radio.setPALevel(RF24_PA_HIGH);
  radio.openReadingPipe(1, pipe);
  radio.startListening();

  memset(receivedData, 0, sizeof(receivedData));
}

void loop() {
  if (radio.available()) {
    byte packet[32] = {0};
    radio.read(&packet, sizeof(packet));

    int id = packet[0];
    int total = packet[1];
    if (totalPackets == -1) totalPackets = total;

    if (!receivedFlags[id]) {
      size_t offset = id * CHUNK_SIZE;
      size_t dataLen = radio.getPayloadSize() - 2;  // actual payload size
      memcpy(receivedData + offset, &packet[2], dataLen);

      receivedFlags[id] = true;
      totalReceived++;
      messageLength += dataLen;
    }

    if (totalReceived == totalPackets) {
      // Serial.println("Data (hex):");

      // for (size_t i = 0; i < messageLength; i++) {
      //   if (receivedData[i] < 0x10) Serial.print("0");
      //   Serial.print(receivedData[i], HEX);
      //   Serial.print(" ");
      //   if ((i + 1) % 16 == 0) Serial.println();
      // }

      // Serial.println();
      Serial.write(receivedData, messageLength);

      // Reset for next message
      totalPackets = -1;
      totalReceived = 0;
      messageLength = 0;
      memset(receivedFlags, 0, sizeof(receivedFlags));
      memset(receivedData, 0, sizeof(receivedData));
      radio.flush_rx();
    }
  }
  delay(100);
}
