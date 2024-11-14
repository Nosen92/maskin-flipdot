These arduino sketches establish a wireless link between a sender node and a receiver node, using NRF 24L01 wireless transceivers.

The MCUs are Wemos D1 minis. You can use any arduino with an SPI interface (MISO, MOSI, SCLK, CS). 
Be aware that while the NRF 24L01 data pins are 5V tolerant, VCC must be 3.3V!

Limitations:
- Commands can't be longer than 32 bytes.
- Checksum fails for checksum = 0xfe and 0xff.

Chip hookup:
| D1 mini | NRF 24L01 | MAX485 (receiver only) |
|:------:|:--------------:|:----:|
| GND | GND | GND |
| 3.3V | VCC |  |
| 5V |  | VCC |  |
| MOSI | MOSI |  |
| MISO | MISO |  |
| SCLK | SCK |  |
| CS | CSN |  |
| GPIO16 (D0) | CE |
| TX |  | DI |
| 5V |  | DE |
| 5V |  | RE |
