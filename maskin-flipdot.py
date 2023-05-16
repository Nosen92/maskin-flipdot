import serial

width = 112
height = 16
address = 0x06 # can also be 0x06 and 0x07
#text = "15   Engineers"
#text = "Det heter byggmacka"
text = "Engineers   15"

def header(address):
    header = bytearray()
    header.append(0xff)  # Header
    header.append(0x06)  # Address
    header.append(0xa2)  # Text node
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
    payload.append(0x0a)

    # Vertical offset:
    payload.append(0xd3)
    payload.append(vertical_offset)

    # Font
    payload.append(0xd4)
    payload.append(0x65)

    """ Different fonts:
    text_5px = 0x72  # Large letters only
    text_6px = 0x66
    text_7px = 0x65
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

    payload.extend(text_str.encode('utf-8'))
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
    with serial.Serial('/dev/ttyS0', 4800, timeout=1) as ser:
        ser.write(payload)


def write(text, address):
    payload = header(address)
    payload = encode(payload, text, 10)
    payload = checksum(payload)
    upload(payload)


def main():
        write(text, address)
        sleep(1)


main()
