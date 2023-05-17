import serial
from time import sleep

from PIL import Image
import numpy as np

width = 112
height = 16
address = 0x06 # can also be 0x06 and 0x07
#text = "15   Engineers"
#text = "Det heter byggmacka"
text = "Hej Elias"

def header(address):
    header = bytearray()
    header.append(0xff)  # Header
    header.append(0x06)  # Address
    header.append(0xa2)  # Text mode
    # Display width
    header.append(0xd0)
    header.append(width)
    # Display height
    header.append(0xd1)
    header.append(height)

    return header


def encode(payload, text_str, horizontal_offset=0, vertical_offset=0, font=0x66):
    # Horizontal offset:
    payload.append(0xd2)
    payload.append(0x00)

    # Vertical offset: offset to bottom of text
    payload.append(0xd3)
    payload.append(vertical_offset)

    # Font
    payload.append(0xd4)
    payload.append(0x77)



    for i in range(112):
        payload.append(32 + 0b00010)

    payload.append(0xd2)
    payload.append(0x00)

    payload.append(0xd3)
    payload.append(0x09)
       # Font
    payload.append(0xd4)
    payload.append(0x77)

    for i in range(112):
        payload.append(32 + 31)


    # for i in range(16):
    #     payload.extend(i)


    """ Different fonts:
    text_5px = 0x72  # Large letters only
    text_7px = 0x66
    text_13px = 0x65
    text_7px_bold = 0x64
    text_9px = 0x75
    text_9px_bold = 0x70
    text_9px_bolder = 0x62
    text_13px = 0x73
    text_13px_bold = 0x69
    text_13px_bolder = 0x61
    text_13px_boldest = 0x79
    numbers_14px = 0x00
    text_15px = 0x71
    text_16px = 0x68
    text_16px_bold = 0x78
    text_16px_bolder = 0x74
    symbols = 0x67
    bitwise = 0x77
"""
    #payload.extend(text_str.encode('utf-8'))
    return payload


def addBits(bits):
    ret = 32
    for i in range(len(bits)):
        ret += bits[i]*2**i
    return ret


def pixelWrite(payload, bitmap):
    # Iterate over every pixel of the sign.
    for i in range(1, height//5 +1):
        # Iterate over all 5px bands in the sign
        payload.append(0xd2)
        payload.append(0x00)

        payload.append(0xd3)
        payload.append(i*5-1)

        payload.append(0xd4)
        payload.append(0x77)


        for j in range(width):
            subcollumn = []
            for k in range((i-1)*5,i*5):
                subcollumn.append(bitmap[k][j])
            
            payload.append(addBits(subcollumn))

    if height%5 != 0:
        payload.append(0xd2)
        payload.append(0x00)

        payload.append(0xd3)
        payload.append(height - height%5 + 5-1)

        payload.append(0xd4)
        payload.append(0x77)
    
        for j in range(width):

            subcollumn = []
            for k in range(height - height%5, height):
                subcollumn.append(bitmap[k][j])
            
            payload.append(addBits(subcollumn))

    return payload

    

def checksum(payload):
    check_sum = 0
    for i in payload[1:]:
        check_sum = check_sum + i

    check_sum = check_sum & 0xff
    if check_sum == 0xfe:
        payload.append(0xfe)
        payload.append(0x00)
    elif check_sum == 0xff:
        payload.append(0xfe)
        payload.append(0x01)
    else:
        payload.append(check_sum)

    payload.append(0xff)
    return payload


def upload(payload):
    with serial.Serial('COM4', 4800, timeout=1) as ser:
        ser.write(payload)


def write(text, image, address):
    payload = header(address)
#    payload = encode(payload, text, 10)
    payload = pixelWrite(payload, picToArray(image))
    payload = checksum(payload)
    upload(payload)





def picToArray(image):
    img = Image.open(image).convert('L')
    newImg = img.resize((112,16))
    np_img = np.array(newImg)
    np_img = ~np_img  # invert B&W
    np_img[np_img > 0] = 1
    img.close()
    return np_img

def main():
    while 1:
        write(text, 'test.png', address)
        sleep(3)
        write(text, 'test2.png', address)
        sleep(3)
        write(text, 'test3.png', address)
        sleep(3)



main()

