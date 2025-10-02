# This module holds general non subsystem specific helper functions and classes
# Created By: Alper Alpcan
# Created Date: 05/09/2025
# version ='1.02'
import time

debugFlag = False

HIGH = 1
LOW = 0
 
lightState = {
    "OFF": 0,
    "RED": 1,
    "YELLOW": 2,
    "GREEN": 3,
    "FLASHING": 4
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

@DeprecationWarning
def flash_color(traffic_light: dict, color: int, flashesPerSec: int) -> None:
    """
    OBSOLETE - use hardware based (555) flashing
    
    Flash the light on/off programmatically 
    
    Parameters:
        traffic_light (dict): The traffic light dictionary.
        color (int): lightState value to flash
        flashesPerSec (int): number of flashes per second
    Returns:
        None
    """
    if int(time.time() * flashesPerSec * 2) % 2 == 0:
        set_tl_state(traffic_light, lightState["OFF"])
    else:
        set_tl_state(traffic_light, color)        
        