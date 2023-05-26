import mobitec
import time
import datetime
import math

def clock():

    #port = "/dev/ttyS0" # RPi
    port = "/dev/ttyUSB0" # Jonas
    #port = "COM4" # Kasper

    fonts = {
            # name, height, code
            "7px": mobitec.Font("7px", 7, 0x60),
            "7px_wide": mobitec.Font("7px_wide", 7, 0x62),
            "12px": mobitec.Font("12px", 12, 0x63),
            "13px": mobitec.Font("13px", 13, 0x64),
            "13px_wide": mobitec.Font("13px_wide", 13, 0x65),
            "13px_wider": mobitec.Font("13px_wider", 13, 0x69),
            "16px_numbers": mobitec.Font("16px_numbers", 16, 0x68),
            "16px_numbers_wide": mobitec.Font("16px_numbers_wide", 16, 0x6a),
            "pixel_subcolumns": mobitec.Font("pixel_subcolumns", 5, 0x77)
    }
    
    # Define the pixel representations for each character
    characters = {
        "0": [
            [1, 1, 1],
            [1, 0, 1],
            [1, 0, 1],
            [1, 0, 1],
            [1, 1, 1]
        ],
        "1": [
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1]
        ],
        "2": [
            [1, 1, 1],
            [0, 0, 1],
            [1, 1, 1],
            [1, 0, 0],
            [1, 1, 1]
        ],
        "3": [
            [1, 1, 1],
            [0, 0, 1],
            [1, 1, 1],
            [0, 0, 1],
            [1, 1, 1]
        ],
        "4": [
            [1, 0, 1],
            [1, 0, 1],
            [1, 1, 1],
            [0, 0, 1],
            [0, 0, 1]
        ],
        "5": [
            [1, 1, 1],
            [1, 0, 0],
            [1, 1, 1],
            [0, 0, 1],
            [1, 1, 1]
        ],
        "6": [
            [1, 1, 1],
            [1, 0, 0],
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1]
        ],
        "7": [
            [1, 1, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1]
        ],
        "8": [
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1]
        ],
        "9": [
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],
            [0, 0, 1],
            [1, 1, 1]
        ],
        ":": [
            [0],
            [1],
            [0],
            [1],
            [0]
        ]
    }

    flipdot = mobitec.MobitecDisplay(port, fonts, address=0x06, width=112, height=16)        

    while True:
    
        clock_face = mobitec.Bitmap(13, 13, 0, 0)
        clock_face.bitmap = [
            [0,0,0,0,1,1,1,1,1,0,0,0,0],
            [0,0,1,1,0,0,0,0,0,1,1,0,0],
            [0,1,0,0,0,0,0,0,0,0,0,1,0],
            [0,1,0,0,0,0,0,0,0,0,0,1,0],
            [1,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,1],
            [0,1,0,0,0,0,0,0,0,0,0,1,0],
            [0,1,0,0,0,0,0,0,0,0,0,1,0],
            [0,0,1,1,0,0,0,0,0,1,1,0,0],
            [0,0,0,0,1,1,1,1,1,0,0,0,0]
        ]
        # Get the current time
        now = datetime.datetime.now()
        hour = now.hour % 12  # Convert to 12-hour format
        minute = now.minute
        second = now.second
        
        hour_x = 6
        hour_y = 6
        minute_x = 6
        minute_y = 6
        second_x = 6
        second_y = 6
        
        # Calculate the end coordinates for each hand using cosine and sine functions
        hour_length = 4
        minute_length = 5
        second_length = 6
        
        hour_angle = math.radians(30 * hour + 0.5 * minute)  # 30 degrees per hour + 0.5 degrees per minute
        minute_angle = math.radians(6 * minute + 0.1 * second)  # 6 degrees per minute + 0.1 degrees per second
        second_angle = math.radians(6 * second)  # 6 degrees per second

        hour_end_x = hour_x + int(hour_length * math.sin(hour_angle))
        hour_end_y = hour_y - int(hour_length * math.cos(hour_angle))
        minute_end_x = minute_x + int(minute_length * math.sin(minute_angle))
        minute_end_y = minute_y - int(minute_length * math.cos(minute_angle))
        second_end_x = second_x + int(second_length * math.sin(second_angle))
        second_end_y = second_y - int(second_length * math.cos(second_angle))

        # Draw the clock hands
        
        draw_line(clock_face.bitmap, hour_x, hour_y, hour_end_x, hour_end_y)
        draw_line(clock_face.bitmap, minute_x, minute_y, minute_end_x, minute_end_y)
        draw_line(clock_face.bitmap, second_x, second_y, second_end_x, second_end_y)
        
        flipdot.print_image(clock_face)
        
        hour = "{:02d}".format(now.hour)
        minute = "{:02d}".format(now.minute)
        
        digital_clock = mobitec.Bitmap(7, 11, 17, 1)
        place_character(digital_clock.bitmap, characters[hour[0]], 0, 0)
        place_character(digital_clock.bitmap, characters[hour[1]], 4, 0)
        place_character(digital_clock.bitmap, characters[minute[0]], 0, 6)
        place_character(digital_clock.bitmap, characters[minute[1]], 4, 6)
        
        flipdot.print_image(digital_clock)
        
        flipdot.display()
        flipdot.clear_display()
        
        time.sleep(0.5)

def draw_line(matrix, x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    
    while x1 != x2 or y1 != y2:
        matrix[y1][x1] = 1
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
    
    matrix[y1][x1] = 1

def place_character(matrix, char_matrix, x, y):
    char_height = len(char_matrix)
    char_width = len(char_matrix[0])

    for i in range(char_height):
        for j in range(char_width):
            matrix[y + i][x + j] = char_matrix[i][j]

clock()
