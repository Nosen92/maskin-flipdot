# Mobitec Sign Protocol

> This document serves to explain the Mobitec protocol. It is not required reading to use the python code, since that handles all this for you.

To control the flipdot display, commands are sent using Mobitec's sign protocol. This protocol is really slow and robust, consists of a sequence of bytes represented here with two hex values: (e.g. 0xab).
Here is an example that simply writes EXAMPLE at the top left of the display:
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
0xcd  # Checksum           ⎫ Footer
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
>TODO: See if resolution config is necessary in every packet.

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
> The lists of fonts available online (in other mobitec project repos) differ from one another, indicating that each display is programmed with a unique set of fonts. Only one font is consistent in all cases: The pixel control font `0x77`.

The complete font list (yours might differ):
```
"7px": 0x60, # Seems to be fallback font, for unknown font codes
"7px_wide": 0x62,
12px": 0x63,
"13px": 0x64,
"13px_wide": 0x65,
"13px_wider": 0x69,
16px_numbers": 0x68,
"16px_numbers_wide": 0x6a,
"pixel_subcolums": 0x77
```

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

> One packet may contain many different data sections, one after the other. But for every data section, **all** parameters (offsets and font) need to be included, even if they are identical to a previous section (in that case they need to be repeated). If any one parameter is omitted, the sign **disregards** that section of data.

## Footer
```
0xcd  # Checksum
0xff  # Stop byte, always ff
```
Every packet ends with a footer, consisting of a checksum and the stop byte `0xff`. The checksum is calculated by adding up all the previous characters in the packet, and taking the lower two bytes of that sum. This is done both on the sender side, and display side. If the two checksums do not match, the display **disregards** the whole packet.
>What happens when the checksum itself is `0xff`? That would conflict with the stop byte. To account for this special case, the checksum is altered to the **two** bytes `0xfe` and `0x01`. Strangely, the checksum is also altered in the case when it's `0xfe`, then it becomes `0xfe` followed by `0x00`.

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
One packet may contain an arbitrary number of data sections. They may all have different offsets and fonts from one another. You can even have overlapping data sections. 
> All pixels that are ordered to be lit by any data section, stay lit. In effect, the sign considers black to be transparent.

