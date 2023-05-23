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
    
    def __init__(self, port, fonts, address, width, height):
        """Makes a display object."""
        self.port = port
        self.address = address
        self.width = width
        self.height = height
        self.fonts = fonts
        self.current_font = fonts["7px"]
        self.cursor = {
            "x": 0,
            "y": 0
        }
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
            text_code = self._text_to_mp(text)
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

    def _text_to_mp(self, text):
        """Converts text string to mobitec protocol.
        Accounts for deviations from ASCII codes."""
        horizontal_offset = text.pos_x
        vertical_offset = text.pos_y + text.font.height  # Compensation for quirky offset
        if text.font.name == "pixel_subcolumns":  # Don't ask me why
            vertical_offset -= 1
        data = self._data_header(text.font.code, horizontal_offset, vertical_offset)
        special_char_mapping = {
            "Å": 0x5d,
            "å": 0x7d,
            "Ä": 0x5b,
            "ä": 0x7b,
            "Ö": 0x5c,
            "ö": 0x7c
        }
        for char in text.string:
            if char in special_char_mapping:
                char = special_char_mapping[char]
            else:
                char = ord(char)
            data.append(char)
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
        with serial.Serial(self.port, 4800, timeout=1) as ser:
            ser.write(packet)
            
    def clear_display(self):
        """Clears the display buffer."""
        self.text_buffer = []
        self.image_buffer = []
        
    def set_cursor(self, x, y):
        self.cursor = {
            "x": x,
            "y": y
        }
        
    def set_font(self, font):
        self.current_font = self.fonts[font]
    
    def print_text(self, string):
        """Adds text to the text buffer."""
        text = Text(string, self.current_font, self.cursor["x"], self.cursor["y"])
        self.text_buffer.append(text)
        
    def dvd_screensaver(self, fps):
        """One pixel bounces off the sides of the display indefinitely."""
        down = True
        right = True
        x = 0
        y = 0
        self.set_font("pixel_subcolumns")
        while True:
            self.clear_display()
            self.set_cursor(x, y)
            self.print_text("!")  # Just top pixel
            self.display()
            sleep(1/fps)
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
            if y == self.height - 1:
                down = False
            if y == 0:
                down = True

class Font:

    def __init__(self, name, height, code):
        self.name = name
        self.height = height
        self.code = code
        
class Text:

    def __init__(self, string, font, pos_x, pos_y):
        self.string = string
        self.font = font
        self.pos_x = pos_x
        self.pos_y = pos_y

if __name__ == "__main__":
    """Example usage."""

    import serial
    #port = "/dev/ttyS0" # RPi
    port = "/dev/ttyUSB0" # Jonas
    #port = "COM4" # Kasper
    
    fonts = {
            # name, height, code
            "7px": Font("7px", 7, 0x60),
            "7px_wide": Font("7px_wide", 7, 0x62),
            "12px": Font("12px", 12, 0x63),
            "13px": Font("13px", 13, 0x64),
            "13px_wide": Font("13px_wide", 13, 0x65),
            "13px_wider": Font("13px_wider", 13, 0x69),
            "16px_numbers": Font("16px_numbers", 16, 0x68),
            "16px_numbers_wide": Font("16px_numbers_wide", 16, 0x6a),
            "pixel_subcolumns": Font("pixel_subcolumns", 5, 0x77)
    }
    flipdot = MobitecDisplay(port, fonts, address=0x0b, width=28, height=13)
    
    flipdot.set_font("13px_wider")
    flipdot.set_cursor(0, 0)
    flipdot.print_text("Test")
    flipdot.display()
    sleep(1)
    flipdot.clear_display()
    flipdot.set_cursor(7, 6)
    flipdot.print_text("text")
    flipdot.display()
    sleep(1)
    flipdot.clear_display()
    flipdot.set_cursor(5, 0)
    flipdot.print_text("Hello")
    flipdot.display()
    sleep(1)
    flipdot.clear_display()
    flipdot.set_cursor(0, 6)
    flipdot.print_text("world")
    flipdot.display()
    sleep(1)
    # Add bitmap example too
    
    
    flipdot.dvd_screensaver(2)

