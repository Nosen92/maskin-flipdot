#include <Arduino.h>
#include <SPI.h>
#include <RF24.h>

RF24 radio(16, 15);  // CE, CSN
const uint64_t pipe = 0xE8E8F0F0E1LL;

const size_t CHUNK_SIZE = 30;        // 32 - 2 header
const size_t MAX_DATA_SIZE = 512;    // Max transmission size

byte serialBuffer[MAX_DATA_SIZE];

void sendByteArray(const byte* data, size_t length) {
  size_t totalPackets = (length + CHUNK_SIZE - 1) / CHUNK_SIZE;

  for (size_t i = 0; i < totalPackets; i++) {
    byte outPacket[32] = {0};
    outPacket[0] = i;
    outPacket[1] = totalPackets;

    size_t offset = i * CHUNK_SIZE;
    size_t len = min(CHUNK_SIZE, length - offset);
    memcpy(&outPacket[2], data + offset, len);

    bool success = radio.writeBlocking(outPacket, len + 2, 500);
    Serial.print("Packet ");
    Serial.print(i);
    Serial.println(success ? " OK" : " FAIL");

    delay(50);
  }

  Serial.println("✅ Transmission complete.");
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  radio.begin();
  radio.setPALevel(RF24_PA_HIGH);
  radio.setRetries(5, 15);
  radio.openWritingPipe(pipe);
  radio.stopListening();

  Serial.println("🟢 Ready to receive data over Serial...");
}

void loop() {
  static size_t index = 0;

  // Read serial input until buffer is full or newline
  while (Serial.available() > 0 && index < MAX_DATA_SIZE) {
    char c = Serial.read();
    if (c == '\n') {
      sendByteArray(serialBuffer, index);
      index = 0;  // reset for next message
      digitalWrite(LED_BUILTIN, HIGH);
      delay(2000);
      digitalWrite(LED_BUILTIN, LOW);
    } else {
      serialBuffer[index++] = (byte)c;
    }
  }
}
