# This module holds general non subsystem specific helper functions and classes
# Created By: Alper Alpcan
# Created Date: 05/09/2025
# version ='1.02'
from pymata4 import pymata4
import time

DEBUG = 0

HIGH = 1
LOW = 0
 
lightState = {
    "OFF": 0,
    "RED": 1,
    "YELLOW": 2,
    "GREEN": 3,
    "FLASHING": 4 # color of flashing is determined through hardware connections of lights
}

def create_traffic_light(name: str, initialState: int) -> dict:
    """
    Creates a new traffic light dictionary.

    Parameters:
        name (str): The name of the traffic light.
        initialState (int): The initial state (color) of the light.
            
    Returns:
        dict: A dictionary representing the traffic light.
    """
    traffic_light = {
        "name": name,
        "state": initialState,
        "stateTimeStarted": time.time()
    }
    return traffic_light


def set_tl_state(traffic_light: dict, newState: int) -> None:
    """
    Sets the traffic light's color state and updates its start time.

    Parameters:
        traffic_light (dict): The traffic light dictionary.
        newState (int): A LightState enum value.
            
    Returns:
        None
    """
    traffic_light["state"] = newState
    traffic_light["stateTimeStarted"] = time.time()


def tl_state_elapsed_time(traffic_light: dict) -> float:
    """
    Calculates the time elapsed since the last state change.

    Parameters:
        traffic_light (dict): The traffic light dictionary.
            
    Returns:
        float: The total time elapsed in its current LightState.
    """
    return time.time() - traffic_light["stateTimeStarted"]

# OBSOLETE
def flash_color(traffic_light: dict, color: int, flashesPerSec: int) -> None:
    """
    OBSOLETE
    """
    if int(time.time() * flashesPerSec * 2) % 2 == 0:
        set_tl_state(traffic_light, lightState["OFF"])
    else:
        set_tl_state(traffic_light, color)        
        
        
def update_shift_register(arduino: pymata4.Pymata4, ser: int, srclk: int, rclk: int, data: int) -> None:
    """
    updates the IC74HC595 shift register. requires SER, SRCLK and RCLK pins to be defined.
    inserts data LSB first.
    
    Parameters:
        ser (int): the serial pin to write from
        srclk (int): the serial clock pin
        rclk (int): the register clock pin
        value (byte): a byte of data to fill the register with.
        
    Returns:
        None
    """
    # pulse register clock low to prepare for data
    arduino.digital_write(rclk, LOW)
    
    for _ in range(8):
        # isolate the LSB
        bit = data & 0b0000_0001
        
        arduino.digital_write(ser, bit)
        
        # write the leftmost bit
        arduino.digital_write(srclk, HIGH)
        arduino.digital_write(srclk, LOW)
        
        # shift to next bit in data
        data >>= 1
    
    # move serial data to register for use
    arduino.digital_write(rclk, HIGH)
        