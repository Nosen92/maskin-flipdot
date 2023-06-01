#scaled down version with only core funtionality
class MobitecDisplay:
    """
    MobitecDisplay is a class that creates display objects, in order 
    to easily communicate with displays using Mobitec's network protocol.
    Attributes:
        address (byte): Hardware address of the display controller.
        width (byte): Horizontal resolution of the display.
        height (byte): Vertical resolution of the display.
        position (dict): Stores position for text placement.
        font (byte): Internal font code to send with the text.
        image_buffer (list of dicts): Stores image data before sending to display.
        text_buffer (list of dicts): Stores Text objects before sending to display.
    Text information is stored as a dict with these keys:
        "string" (string): Text string to be written.
        "font" (byte): What font to use.
        "offset_x" (byte): Horizontal offset of text.
        "offset_y" (byte): Vertical offset of text.
    """
    
    def __init__(self, fonts, address, width, height):
        """Makes a display object."""
        self.address = address
        self.width = width
        self.height = height
        self.fonts = fonts
        self.current_font = fonts["7px"]
        self.position = {
            "x": 0,
            "y": 0
        }
        self.image_buffer = []
        self.text_buffer = []
        
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
            image_code = self._bitmap_to_mp(image)
            packet.extend(image_code)
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
        """Serializes text object to mobitec protocol.
        Accounts for deviations from ASCII codes."""
        horizontal_offset = text.pos_x
        vertical_offset = text.pos_y + text.font.height  # Compensation for quirky offset
        if text.font.name == "pixel_subcolumns":
            vertical_offset -= 1  # Don't ask me why
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
        
    def _bitmap_to_mp(self, bitmap):
        """Serializes bitmap to mobitec protocol."""
        data = bytearray()
        mobitec_subcolumn_matrix = bitmap.convert_to_sm()
        for band in range(len(mobitec_subcolumn_matrix)):
            data_header = self._data_header(0x77, bitmap.pos_x, bitmap.pos_y + band * 5 + 4)
            data.extend(data_header)
            for subcolumn in range(bitmap.width):
                subcolumn_code = self.addBits(mobitec_subcolumn_matrix[band][subcolumn])
                data.append(subcolumn_code)
        return data

    def addBits(self, bits):
        ret = 32
        for i in range(len(bits)):
            ret += bits[i]*2**i
        return ret

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
        
    def display(self, uart):
        """Sends contents of the buffer to the display."""
        packet = self._create_packet()
        uart.write(packet)
            
    def clear_display(self):
        """Clears the display buffer."""
        self.text_buffer = []
        self.image_buffer = []
        
    def set_position(self, x, y):
        """Set the x y position."""
        self.position = {
            "x": x,
            "y": y
        }
        
    def set_font(self, font):
        """Chooses font to write text with."""
        self.current_font = self.fonts[font]
    
    def print_text(self, string):
        """Adds text to the text buffer."""
        text = Text(string, self.current_font, self.position["x"], self.position["y"])
        self.text_buffer.append(text)
        
    def print_image(self, image):
        """Adds text to the text buffer."""
        self.image_buffer.append(image)
        
        
class Font:
    """
    Basic font objects.
    Attributes:
        name (string): Name of font.
        height (byte): Height of the font. Used for position glitch fix.
        code (byte): Font code used by the sign. Between 0x60 - 0x80.
    """
    def __init__(self, name, height, code):
        self.name = name
        self.height = height
        self.code = code
        
class Text:
    """
    Basic text objects. Gets queued in the buffer.
    Attributes:
        string (string): Text to be written.
        font (Font): Font to write the text with.
        pos_x (byte): Horizontal offset from left side.
        pos_y (byte): Vertical offset from upper side.
    """
    def __init__(self, string, font, pos_x, pos_y):
        self.string = string
        self.font = font
        self.pos_x = pos_x
        self.pos_y = pos_y
        
class Bitmap:
    """
    Basic bitmap objects. Gets queued in the image buffer.
    Attributes:
        width (byte): Bitmap width.
        height (byte): Bitmap height.
        pos_x (byte): Horizontal offset from left side.
        pos_y (byte): Vertical offset from upper side.
        bitmap (list of lists): Bitmap. Adressed like this: bitmap[y][x]
    """
    def __init__(self, width, height, pos_x, pos_y):
        self.width = width
        self.height = height
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.bitmap = [[False] * self.width for _ in range(self.height)]  # Create x*y matrix
    
    def convert_to_sm(self):
        """Converts a regular bitmap to subcolumn matrix."""
        subcolumn_matrix = []
        for full_bands in range(self.height//5):
            band = []
            for subcolumns in range(self.width):
                subcolumn = []
                for subcolumn_pixel in range(5):
                    subcolumn.append(self.bitmap[full_bands * 5 + subcolumn_pixel][subcolumns])
                band.append(subcolumn)
            subcolumn_matrix.append(band)
        if self.height%5 != 0:
            band = []
            for subcolumns in range(self.width):
                subcolumn = []
                for subcolumn_pixel in range(self.height - self.height%5, self.height):
                    subcolumn.append(self.bitmap[subcolumn_pixel][subcolumns])
                band.append(subcolumn)
            subcolumn_matrix.append(band)
        return subcolumn_matrix
    
    def __eq__(self, other):
        for y in range(0, self.height):
            for x in range(0, self.width):
                try:
                    if self.bitmap[y][x] != other.bitmap[y][x]:
                        return False
                except Exception as e:
                    print("Error!")
                    print(e)
                    return False
        return True
        

