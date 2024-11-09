# Mobitec Sign Protocol

> [!NOTE] 
> This document serves to explain the Mobitec protocol. It is not required reading to use the python or arduino code, since that handles all this for you.

To control the flipdot display, commands are sent as a sequence of bytes using Mobitec's sign protocol. This protocol is really robust, but very slow. Display refresh rate is 1-2 fps.

The byte sequence is sent to the sign via serial communication at 4800 Baud using the common 8N1 config (one start bit, eight data bits, no parity bit, and one stop bit) using the old serial communication standard [RS-485](https://en.wikipedia.org/wiki/RS-485). You can use a cheap MAX485 module to convert ordinary serial UART data to RS-485 in order to communicate with the sign.

The sign only receives data and does not respond with any data (as far as I'm aware, I haven't really been listening).

I call byte sequences packets in this documentation. Here is a packet that simply writes EXAMPLE on the top left of the display:
```
0xff  # Starting byte      ⎫
0x06  # Sign address       ⎟
0xa2  # Always a2          ⎟
0xd0  # Display width      ⎬ Header
0x70  # 112px              ⎟
0xd1  # Display height     ⎟
0x10  # 16px               ⎭
0xd2  # Horizontal offset  ⎫
0x00  # 0px right          ⎟
0xd3  # Vertical offset    ⎟
0x0d  # 13px down          ⎟
0xd4  # Font               ⎟
0x73  # 13px font          ⎟
0x45  # E                  ⎬ Data
0x58  # X                  ⎟
0x41  # A                  ⎟
0x4d  # M                  ⎟
0x50  # P                  ⎟
0x4c  # L                  ⎟
0x45  # E                  ⎭
0xce  # Checksum           ⎫ Footer
0xff  # Stop byte          ⎭
```
Each packet can be divided into these parts: **header**, **data**, and **footer**. Let's break it down.

## Header
```
0xff  # Starting byte, always ff
0x06  # Sign address, front signs are 0x06, side signs 0x07 and back signs 0x0a or 0x0b
0xa2  # Always a2 (referred to as text mode)
0xd0  # Display width label
0x70  # 112 pixels wide (0x70 = 112 in decimal)
0xd1  # Display height label
0x10  # 16 pixels wide (0x10 = 16 in decimal)
```
This part only needs to be sent once per packet. 

> TODO: Investigate the purpose of `0xa2`.

### Address
```
0x06  # Sign address, configurable on sign via coded rotary switch on sign PCB
```
The address byte in the packet header needs to match the hardware address of the sign.
Why? Presumably, all destination signs in a bus share one control unit that's operated by the driver. Going forward in this text, whenever I write "bus" I'm referring to the data output pins of that sign control unit. If all signs are probably connected to the same data bus, what do we do if we want the name of the end-of-the-line stop on the front sign but only the line number on the back sign? Since the signs only recognize commands that have their address byte, all signs can share and receive all packets on the bus, and choose to ignore the ones that are not indended for them.

The sign address can be read by inspecting the coded rotary switch on the sign's internal PCB (behind a small access panel). The sign's address can of course be changed by turning this switch. All values between `0x00` and `0x0f` are available, making the theoretical maximum of signs on the same bus 16. If you have more signs than that, please give some of them to me.

### Resolution

```
0xd0  # Display width label
0x70  # 112 pixels wide (0x70 = 112 in decimal)
0xd1  # Display height label
0x10  # 16 pixels wide (0x10 = 16 in decimal)
```

For whatever reason, you can provide the sign with resolution data. I have not found the usecase for this and the sign will work without this data in every packet. All displays I have seen have been either 112x16 or 28x13.

> More research about the usefulness of the resolution part could be beneficial.

## Data
The data contains information about what to draw and where. Every data section **is required** to include an offset and font data, or it will be disregarded by the sign.

### Horizontal and vertical offset
```
0xd2  # Text cursor horizontal offset label
0x00  # Horizontal offset = 0
0xd3  # Text cursor vertical offset label
0x0d  # Vertical offset = 13, bottom left of character
```
The sign features an offset capability that allows both rightward and downward shifting of the text (the usual 4th quadrant screen coordinates). However, the vertical offset works in a weird way. The sign starts writing each character from its bottom-left corner. For example, applying a 13px vertical offset to a 5px font will create a 8px gap between the top of the 5px high character and the top of the display.

Furthermore, it's important to note that the sign **disregards** any vertical offsets that would cause a character to exceed the top boundary of the display. This means that to move a 7px character 2px downwards, a 9px offset must be applied. If the offset is set to 2px, the text will appear at the top of the screen. On the other hand, the sign appropriately crops any text that exceeds the display boundaries downward or to the right, as expected.

### Font selection
```
0xd4  # Font selection label
0x73  # 13px text font
```
This part instructs the display on which font to use for writing the text.

>[!NOTE]
> The lists of fonts available online (in other mobitec project repos) differ from one another, indicating that displays are programmed with different set of fonts. Only one font is consistent in all cases: The pixel control font `0x77`.

The complete font list (yours might differ):

|  Code  |         Font         |
|:------:|:--------------------:|
| `0x60` |        `7 px`        |
| `0x62` |     `7 px wide`      |
| `0x63` |       `12 px`        |
| `0x64` |       `13 px`        |
| `0x65` |     `13 px wide`     |
| `0x69` |    `13 px wider`     |
| `0x68` |   `16 px numbers`    |
| `0x6a` | `16 px numbers wide` |
| `0x77` |   `Pixel control`    |

The 7px font seems to be the fallback font when entering something not on this list.

More info on pixel control in the 'Pixel Control with subcolumns' section.


### Text
```
0x45  # E
0x58  # X
0x41  # A
0x4d  # M
0x50  # P
0x4c  # L
0x45  # E
```
The text is fairly basic ASCII codes. ASCII codes that are not recognized by the display are disregarded.

Some ASCII characters are replaced by swedish diacritic characters (Same as ["SvASCII"](https://www.wikiwand.com/en/articles/Code_page_1018)).
| Char |  Byte  | ASCII |
|:----:|:------:|:-----:|
|   Å  | `0x5d` |   ]   |
|   å  | `0x7d` |   }   |
|   Ä  | `0x5b` |   [   |
|   ä  | `0x7b` |   {   |
|   Ö  | `0x5c` |   \   |
|   ö  | `0x7c` |   \|  |


>[!IMPORTANT]
> One packet may contain many different data sections, one after the other. But for every data section, **all** parameters (offsets and font) need to be included, even if they are identical to a previous section (in that case they need to be repeated). If any one parameter is omitted, the sign **disregards** that section of data!

## Footer and checksum
```
0xcd  # Modulo 256 Checksum
0xff  # Stop byte, always ff
```
Every packet ends with a footer, consisting of a modulo 256 checksum and the stop byte `0xff`. The checksum is calculated by adding up all the previous characters in the packet (excluding the start byte `0xff`), then performing a modulo 256 operation, which in effect gets rid of every byte of that sum except the least significant byte. The remaining byte is the checksum. This is done both on the sender side, and display side. If the two checksums do not match, the display **disregards** the whole packet.
>What happens when the checksum itself is `0xff`? That would conflict with the stop byte. To account for this special case, the checksum is altered to the **two** bytes `0xfe` and `0x01`. Curiously, the checksum is also altered in the case when it's `0xfe`, then it becomes `0xfe` followed by `0x00`.

Then, the stop byte caps off the packet, letting the sign know that transmission of the packet is completed.

## Pixel Control with subcolumns
To enable custom designs on the display, you can enter font code 0x77, which allows individual pixel control. This mode, or rather font, allows for any design on the display. It's not that elegantly implemented in the controller though. Instead of individual pixels or traditional letters, this font represents a 5-pixel high design, where each character is only 1 pixel wide. We call these **subcolumns**. Every possible combination of these 5 pixels is assigned a unique character code. Compare with [sixels](https://en.m.wikipedia.org/wiki/Sixel) (Maybe the 32 is added to be compatible with sixel char codes?).

This number is obtained like this: Assign 1 to the top pixel, 2 to the second one, 4 to the third, 8 to the 4th and 16 to the 5th. Add up the pixels that should be 'lit'. Then add 32. The sum is that character's code. By iterating over the display 5 rows at a time, the whole display can be drawn in any design.

```
⚫ -  1
⚪ -  2
⚫ -  4
⚪ -  8
⚪ - 16
```
In the above example, we want pixels 2, 8 and 16 to be lit up. The character code needed is 2 + 8 + 16 + 32 = 58 = 0x3a. If we only want the top pixel to be lit, the character code is 1 + 32 = 33 = 0x21.

These six bytes:
```
0x20
0x2a
0x20
0x31
0x2e
0x20
```
make up this smiley face:
```
⚫⚫⚫⚪⚫⚫
⚫⚪⚫⚫⚪⚫
⚫⚫⚫⚫⚪⚫
⚫⚪⚫⚫⚪⚫
⚫⚫⚫⚪⚫⚫
```
Designs taller than 5px are of course possible by dividing the design into 5px bands and then writing one data section for each band.

## Multiple data sections
One packet may contain an arbitrary number of data sections. They may all have different offsets and fonts from one another. You can even have data sections that write overlapping designs on the display. 

> [!NOTE]
> All pixels that are ordered to be lit by any data section, stay lit. In effect, the sign considers black to be transparent.

