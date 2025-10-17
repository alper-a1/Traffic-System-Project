# Created By : Nevinka Serasinghe
# Last Modified: 10/10/2025
# version = 1.6

# revised by Alper 14/10/2025 for integration

import time

overHeightLimit = 40     

# state saves
us1OverHeight = [False,0]
us2OverHeight = [False,0]
tl1State = ["green",0]
tl2State = ["green",0]
pa1State = ["off",0]

# variable for overheight calculations                                                                                                                                                                                                                             
overHeight = 0
sensorToRoadHeight = 60

# delays
tl12RedLightTime = 30
tl12YellowLightTime = 1
us1ToUs2Timing = 5 

# callbacks for us1 and us2
def us1_callback(data):
    """
    when us1 detects a change, call this to interpret the data and set detection accordingly
    Args:
        data: list of data from ultrasonic sensor
    Returns:
        None
    """
    global overHeight
    # when the vehicle is overheight and not already detected
    vehicleHeight = sensorToRoadHeight - data[2]
    if us1OverHeight[0] == False and vehicleHeight > overHeightLimit:
        us1OverHeight[0] = True
        us1OverHeight[1] = time.time()
        overHeight = vehicleHeight
        
    # when the detected overheight vehicle moves away
    if vehicleHeight < overHeightLimit and us1OverHeight[0] == True:
        us1OverHeight[0] = False
        overHeight = 0

def us2_callback(data):
    """
    when us2 detects a change, call this to interpret the data and set detection accordingly
    Args:
        data: list of data from ultrasonic sensor
    Returns:
        None
    """
    # when the vehicle is overheight and not already detected
    vehicleHeight = sensorToRoadHeight - data[2]
    if us2OverHeight[0] == False and vehicleHeight > overHeightLimit:
        us2OverHeight[0] = True
        us2OverHeight[1] = time.time()

    # when the detected overheight vehicle moves away
    if vehicleHeight < overHeightLimit and us2OverHeight[0] == True:
        us2OverHeight[0] = False

# gets the binary data we need to enter into the shift register in order to diaplay what we want
def generate_71_sr_data(tl1,tl2,pa1):
    """
    calculate what value should be fed to the shift register depending on the 2 traffic lights states
    Args:
        tl1: State of Tl1 traffic light
        tl2: State of Tl2 traffic light
        pa1: State of PA1 Buzzer
    Returns:
        data: chunk of binary data to be fed to shift register
    """
    # binary version of 6 leds plus 2 blanks for shift register
    tl1Red     = 0b01000000
    tl1Yellow  = 0b00100000
    tl1Green   = 0b00010000
    tl2Red     = 0b00001000
    tl2Yellow  = 0b00000100
    tl2Green   = 0b00000010
    pa1Low  = 0b10000000
    pa1High = 0b00000001
    
    # reset to nothing on
    data = 0b00000000
    # turn on lights and alarms depending
    match tl1:
        case "green": data |= tl1Green
        case "yellow": data |= tl1Yellow
        case "red": data |= tl1Red
    match tl2:
        case "green": data |= tl2Green
        case "yellow": data |= tl2Yellow
        case "red": data |= tl2Red
    match pa1:
        case "high": data |= pa1High
        case "low": data |= pa1Low
    return data
