import gspread
import serial
import mobitec
import time

def drive_to_bitmap(sheet_name="Flip Dot Code Generator", worksheet_name="ut28x13", width=112, height=16):
    """Requires a gspread service key, only kasper has one"""
    
    #Google sheet: https://docs.google.com/spreadsheets/d/18SiSeSraX6rx-ywxVBl0WOyGEI1JdRoLcY7699Y3k_U/edit?fbclid=IwAR2jnb5gWQbeTzAZwJJPDlf9KJpwlD9il3ta9T7Z5xMizKjno6-QchTXLVg#gid=255959702
    #Note: google services account required, ask Kasper
    try:
        gc = gspread.service_account()

        sh = gc.open(sheet_name)
        arr = sh.worksheet(worksheet_name).get_all_values()
        bm = mobitec.Bitmap(width, height, 0, 0)  # Initialize bitmap
        for j in range(0, len(arr)):
            for i in range(0, len(arr[j])):
                if arr[j][i] == "1":
                    bm.bitmap[j][i] = 1
                elif arr[j][i] == "0":
                    bm.bitmap[j][i] = 0
        return bm
    except Exception as e: #if google failed
        print("Sheet download failed:")
        print(e)
        return None


def drive_display():
    #port = "/dev/ttyS0" # RPi
    #port = "/dev/ttyUSB0" # Jonas
    port = "COM4" # Kasper

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

    flipdot = mobitec.MobitecDisplay(port, fonts, address=0x06, width=112, height=16)    
    old_bm = None

    while(True):
        bm = drive_to_bitmap(worksheet_name="ut112x16", height = 16)
        if bm: #if drive download failed
            if bm != old_bm:
                print("New Data!")
                flipdot.print_image(bm)
                    
                flipdot.display()
                flipdot.clear_display()
                old_bm = bm
        time.sleep(2)



drive_display()
