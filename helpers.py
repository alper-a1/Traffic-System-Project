# This module holds general non subsystem specific helper functions and classes
# Created By: Alper Alpcan
# Created Date: 05/09/2025
# version ='1.02'
import time

debugFlag = False

high = 1
low = 0
 
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
    trafficLight = {
        "name": name,
        "state": initialState,
        "stateTimeStarted": time.time()
    }
    return trafficLight


def set_tl_state(trafficLight: dict, newState: int) -> None:
    """
    Sets the traffic light's color state and updates its start time.

    Parameters:
        traffic_light (dict): The traffic light dictionary.
        newState (int): A LightState enum value.
            
    Returns:
        None
    """
    trafficLight["state"] = newState
    trafficLight["stateTimeStarted"] = time.time()


def tl_state_elapsed_time(trafficLight: dict) -> float:
    """
    Calculates the time elapsed since the last state change.

    Parameters:
        traffic_light (dict): The traffic light dictionary.
            
    Returns:
        float: The total time elapsed in its current LightState.
    """
    return time.time() - trafficLight["stateTimeStarted"]


def get_user_overheight_threshold() -> int:
    """
    Prompts the user to enter an overheight threshold value.
    
    Parameters:
        None
        
    Returns:
        overheightThreshold (int): The overheight threshold value entered by the user, or a default value if no valid input is provided.
    
    """
    threshold = 20 # default of 20 cm
    
    while True:
        userInput = input("Enter an overheight threshold (a number; ie: '15'): ")
        
        if userInput in "\t\n ":
            print("No input detected, using default of 20")
            break
        
        try:
            intInput = int(userInput)
            if intInput <=0:
                raise ValueError
            
            threshold = intInput
            break
        except ValueError:
            print("Please only user valid integers (ie: '20'), try again.")
            
    return threshold

