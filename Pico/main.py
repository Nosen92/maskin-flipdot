from phew import logging, server, access_point, dns
from phew.template import render_template
from phew.server import redirect
from machine import UART, Pin
import mobitecMini as mobitec

uart1 = UART(1, baudrate=4800, tx=Pin(4), rx=Pin(5))

DOMAIN = "pico.wireless"  # This is the address that is shown on the Captive Portal

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
flipdot = mobitec.MobitecDisplay(fonts, address=0x06, width=28, height=16)

def signUpload(binaryString):
    bm = mobitec.Bitmap(112, 16, 0, 0)  # Initialize bitmap
    binaryRows = binaryString.split(";")
    binaryRows.pop()
    print(len(binaryRows))
    for y in range(0,len(binaryRows)):
        print(len(binaryRows[y]))
        for x in range(0, len(binaryRows[y])):
            if binaryRows[y][x] == "1":
                    bm.bitmap[y][x] = 1
            elif binaryRows[y][x] == "0":
                    bm.bitmap[y][x] = 0
                
    flipdot.print_image(bm)
                    
    flipdot.display(uart1)
    flipdot.clear_display()   
            
    


@server.route("/", methods=['GET'])
def index(request):
    """ Render the Index page"""
    if request.method == 'GET':
        logging.debug("Get request")
        return render_template("index2.html")
    
@server.route("/jquery.js")
def handle_jquery(request):
    logging.debug("Jquery request")
    return server.FileResponse("jquery.js")

@server.route("/upload", methods=['POST'])
def handle_upload(request):
    #logging.debug("Upload request: ", request)
    #print(request.form)
    #file = request.files['file']
    #file.save('/file.txt')

    binaryString = request.form.get("binaryString", "0")
    signUpload(binaryString)
    
    return render_template("index2.html")        


@server.catchall()
def catch_all(request):
    logging.debug("Cathall request: ", request)
    return redirect("http://" + DOMAIN + "/")


# Set to Accesspoint mode
# Change this to whatever Wifi SSID you wish
ap = access_point("Pico")
ip = ap.ifconfig()[0]
# Grab the IP address and store it
logging.info(f"starting DNS server on {ip}")
# # Catch all requests and reroute them
dns.run_catchall(ip)
server.run()                            # Run the server
logging.info("Webserver Started")


