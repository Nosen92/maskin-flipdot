from time import sleep  # Only used for dvd screensaver and examples

class MobitecDisplay:
    """MobitecDisplay is a class that creates display objects, in order 
    to easily communicate with displays using Mobitec's network protocol.
    Attributes:
        address (byte): Hardware address of the display controller.
        width (byte): Horizontal resolution of the display.
        height (byte): Vertical resolution of the display.
        cursor (dict): Stores cursor position for text placement.
        font (byte): Internal font code to send with the text.
        image_buffer (list of dicts): Stores image data before sending to display.
        text_buffer (list of dicts): Stores text data before sending to display.
    Text information is stored as a dict with these keys:
        "string" (string): Text string to be written.
        "font" (byte): What font to use.
        "offset_x" (byte): Horizontal offset of text.
        "offset_y" (byte): Vertical offset of text.
    """
    
    def __init__(self, address, width, height):
        """Makes a display object."""
        self.address = address
        self.width = width
        self.height = height
        self.cursor = {
            "x": 0,
            "y": 0
        }
        self.font = 0x60  # 7px default font
        self.image_buffer = []
        self.text_buffer = []
        
    def __bytes__(self):
        packet = self._create_packet()
        return packet
        
    def _create_packet(self):
        """Serializes all data and generates a complete Mobitec packet."""
        packet = bytearray()
        packet.append(0xff) # Start byte
        header = self._packet_header()
        packet.extend(header)
        for text in self.text_buffer:
            string = text["string"]
            font = text["font"]
            offset_x = text["offset_x"]
            offset_y = text["offset_y"]
            text_code = self._text_to_mp(string, font, offset_x, offset_y)
            packet.extend(text_code)
        for image in self.image_buffer:
            string = image["bitmap"]
            offset_x = text["offset_x"]
            offset_y = text["offset_y"]
            self._bitmap_to_mp(string, font, offset_x, offset_y)
        check_sum_byte = self._calculate_check_sum(packet)
        packet.extend(check_sum_byte)
        packet.append(0xff) # Stop byte
        
        return packet

    def _calculate_check_sum(self, packet):
        """Algorithm is: add up all bytes (except start byte). The least significant byte is the check sum. 
        Special cases for 0xfe and 0xff."""
        packet_sum = 0
        for byte in packet[1:]:
            packet_sum = packet_sum + byte
        packet_sum = packet_sum & 0xff
        
        check_sum = bytearray()
        if packet_sum == 0xfe:
            check_sum.append(0xfe)
            check_sum.append(0x00)
        elif packet_sum == 0xff:
            check_sum.append(0xfe)
            check_sum.append(0x01)
        else:
            check_sum.append(packet_sum)
        return check_sum

    def _text_to_mp(self, text, font, horizontal_offset, vertical_offset):
        """Converts text string to mobitec protocol.
        Accounts for deviations from ASCII codes."""
        data = self._data_header(font, horizontal_offset, vertical_offset)
        special_char_mapping = {
            "Å": 0x5d,
            "å": 0x7d,
            "Ä": 0x5b,
            "ä": 0x7b,
            "Ö": 0x5c,
            "ö": 0x7c
        }
        try:
            for char in text:
                if char in special_char_mapping:
                    char = special_char_mapping[char]
                else:
                    char = ord(char)
                data.append(char)
        except TypeError:
            #print("Warning, _text_to_mp raised TypeError. Appending directly.")
            data.append(text)
        return data
        
    def _bitmap_to_mp(self, text, font, horizontal_offset, vertical_offset):
        """Converts bitmap matrix to mobitec protocol."""
        data = bytearray()
        bitwise_fontcode = 0x77
        for i in range(1, height//5 +1):
            data_header = self._data_header(bitwise_fontcode, horizontal_offset, vertical_offset=i*5-1)
            data.extend(data_header)
            
        

        return data

    def _data_header(self, font, horizontal_offset, vertical_offset):
        """Generates mobitec protocol data section header."""
        header = bytearray()
        header.append(0xd2)
        header.append(horizontal_offset)
        header.append(0xd3)
        header.append(vertical_offset)
        header.append(0xd4)
        header.append(font)
        return header

    def _packet_header(self):
        """Generates mobitec protocol packet header."""
        header = bytearray()
        header.append(self.address)
        header.append(0xa2) # Text mode
        header.append(0xd0)
        header.append(self.width)
        header.append(0xd1)
        header.append(self.height)
        return header
        
    def display(self):
        packet = self._create_packet()
        with serial.Serial(port, 4800, timeout=1) as ser:
            ser.write(packet)
            
    def clear_display(self):
        """Clears the display buffer."""
        self.text_buffer = []
        self.image_buffer = []
        return
        
    def set_cursor(self, x, y):
        self.cursor = {
            "x": x,
            "y": y
        }
        return
        
    def set_font(self, font):
        fonts = {
            "7px": 0x60, # Seems to be fallback font, for unknown font codes
            "7px_wide": 0x62,
            "12px": 0x63,
            "13px": 0x64,
            "13px_wide": 0x65,
            "13px_wider": 0x69,
            "16px_numbers": 0x68,
            "16px_numbers_wide": 0x6a,
            "pixel_subcolums": 0x77
        }
        self.font = fonts[font]
        return
    
    def print_text(self, string):
        """Adds text to the text buffer."""
        text = {
            "string": string,
            "font": self.font,
            "offset_x": self.cursor["x"],
            "offset_y": self.cursor["y"]
        }
        self.text_buffer.append(text)
        
    def dvd_screensaver(self):
        """One pixel bounces off the sides of the display indefinitely."""
        down = True
        right = True
        x = 0
        y = 4
        self.set_font("pixel_subcolums")
        while True:
            self.clear_display()
            self.cursor["x"] = x
            self.cursor["y"] = y
            self.print_text(33)  # Just top pixel
            self.display()
            sleep(0.3)
            if right:
                x = x + 1
            else:
                x = x - 1
            if down:
                y = y + 1
            else:
                y = y - 1
            if x == self.width - 1:
                right = False
            if x == 0:
                right = True
            if y == self.height + 3:
                down = False
            if y == 4:
                down = True
             
if __name__ == "__main__":
    """Example usage."""

    import serial
    #port = "/dev/ttyS0" # RPi
    port = "/dev/ttyUSB0" # Jonas
    #port = "COM4" # Kasper
    
    flipdot = MobitecDisplay(address=0x0b, width=28, height=13)
    flipdot.set_font("7px")
    flipdot.set_cursor(1, 6)
    flipdot.print_text("Test")
    flipdot.set_cursor(14, 13)
    flipdot.print_text("text")
    flipdot.display()
    sleep(2)
    flipdot.clear_display()
    flipdot.set_cursor(14, 6)
    flipdot.print_text("Hello")
    flipdot.set_cursor(1, 13)
    flipdot.print_text("world")
    flipdot.display()
    sleep(2)
    # Add bitmap example too
    flipdot.dvd_screensaver()

