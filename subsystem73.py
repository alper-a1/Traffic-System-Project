# subsystem73.py
# Created By: Alper Alpcan
# Created Date: 05/09/2025
# version =1.04

import time

from helpers import *

us5TrigPin = 12
us5EchoPin = 13

def us5_sonar_callback(data):
    """
    callback function for US5, exists for debugging.
    
    Parameters:
        data (int): distance read (in cm) from US5.
        
    Returns:
        None
    """
    if debugFlag:
        print("US5: ", data[2])


def vehicle_exit_handle_idle(vehicleExitStateMachine: dict, elapsedTime: float, us5data: int) -> None:
    """
    Idle state; since VehicleExit has no action for being idle other than waiting to start, this state simply exists for readability / debug.
    
    Parameters:
        vehicleExitStateMachine (dict): The dictionary containing the state machine's variables.
        elapsedTime (float): seconds elapsed in the current state.
        us5data (int): distance read (in cm) from US5.
            
    Returns:
        None 
    """
    pass


def vehicle_exit_handle_start_delay(vehicleExitStateMachine: dict, elapsedTime: float, us5data: int) -> None:
    """
    Idle state; since VehicleExit has no action for being idle other than waiting to start, this state simply exists for readability / debug.
    
    Parameters:
        vehicleExitStateMachine (dict): The dictionary containing the state machine's variables.
        elapsedTime (float): seconds elapsed in the current state.
        us5data (int): distance read (in cm) from US5.
            
    Returns:
        None 
    """
    #3.I1 delay of 3 seconds
    if elapsedTime >= vehicleExitStateMachine['tl6StartDelaySec']:
        set_tl_state(vehicleExitStateMachine['tl6'], lightState["GREEN"])
        
        vehicleExitStateMachine['state'] = 'green'
        vehicleExitStateMachine['stateTimeStarted'] = time.time()
        



def vehicle_exit_handle_green(vehicleExitStateMachine: dict, elapsedTime: float, us5data: int) -> None:
    """
    Handler for the green state. The exit sequence stays on this state for 5 seconds.
    
    Parameters:
        vehicleExitStateMachine (dict): The dictionary containing the state machine's variables.
        elapsedTime (float): seconds elapsed in the current state.
        us5data (int): distance read (in cm) from US5.
            
    Returns:
        None 
    """

    # go to next state after tl6GreenDurationSec seconds
    if elapsedTime >= vehicleExitStateMachine['tl6GreenDurationSec']:
        set_tl_state(vehicleExitStateMachine['tl6'], lightState["FLASHING"])

        vehicleExitStateMachine['state'] = 'flashing'
        vehicleExitStateMachine['stateTimeStarted'] = time.time()
        
        
def vehicle_exit_handle_flashing(vehicleExitStateMachine: dict, elapsedTime: float, us5data: int) -> None:
    """
    handler for the flashing state. The exit sequence stays on this state for at least 3 seconds,
    
    Parameters:
        vehicleExitStateMachine (dict): The dictionary containing the state machine's variables.
        elapsedTime (float): seconds elapsed in the current state.
        us5data (int): distance read (in cm) from US5.
            
    Returns:
        None  
    """
    # this state goes for as long as the overheight is detected 
    if us5data <= vehicleExitStateMachine['overheightLimit']:
        set_tl_state(vehicleExitStateMachine['tl6'], lightState["RED"])
        
        vehicleExitStateMachine['active'] = False
        vehicleExitStateMachine['state'] = 'idle' 
        
        
def create_vehicle_exit(tl6: dict, overheightLimit: int) -> dict:
    """
    Initializes and returns a new state dictionary for the vehicle exit sequence.
    
    Parameters:
        tl6 (dict): The traffic light 6 state dictionary.
        overheightLimit (int): The overheight distance threshold in cm.
        
    Returns:
        dict: A dictionary representing the entire vehicle exit state machine.
    """
    vehicleExitStateHandlers = {
        'idle': vehicle_exit_handle_idle,
        'start_delay': vehicle_exit_handle_start_delay,
        'green': vehicle_exit_handle_green,
        'flashing': vehicle_exit_handle_flashing
    }

    return {
        'tl6': tl6,
        'overheightLimit': overheightLimit,
        'tl6GreenDurationSec': 5,
        'tl6StartDelaySec': 3,
        'active': False,
        'state': 'idle', # intial state
        'stateTimeStarted': 0,
        'vehicleExitStateHandlers': vehicleExitStateHandlers
    }


def start_vehicle_exit(vehicleExitStateMachine: dict) -> None:
    """
    Starts the overheight vehicle exit sequence.
    
    Parameters:
        vehicleExitStateMachine (dict): The dictionary containing the state machine's variables.
        
    Returns:
        None
    """
    if not vehicleExitStateMachine['active']:
        vehicleExitStateMachine['active'] = True
        print("US5 overheight detected, starting vehicle exit sequence")

        vehicleExitStateMachine['state'] = 'start_delay' 
        vehicleExitStateMachine['stateTimeStarted'] = time.time()
    else:
        # since start the sequence is called in a loop, ignore if already active - would create spam in console otherwise
        if debugFlag:
            print("Vehicle exit sequence already active, ignoring start request")


def update_vehicle_exit_sequence(vehicleExitStateMachine: dict, us5data: int) -> None:
    """
    Runs and/or updates the current state if the sequence is active.
    
    Parameters:
        vehicleExitStateMachine (dict): The dictionary containing the state machine's variables.
        us5data (int): distance read (in cm) from US5.
        
    Returns:
        None
    """
    if not vehicleExitStateMachine['active']:
        return
    
    currentTime = time.time()
    elapsedTime = currentTime - vehicleExitStateMachine['stateTimeStarted']

    # Get the handler for the current state from the dispatch table
    handler = vehicleExitStateMachine['vehicleExitStateHandlers'][vehicleExitStateMachine['state']]
    if handler:
        handler(vehicleExitStateMachine, elapsedTime, us5data)


def get_user_overheight_threshold() -> int:
    threshold = 20 # default of 20 cm
    
    while True:
        userInput = input("Enter an overheight threshold (a number; ie: '15'): ")
        
        if userInput in "\t\n ":
            print("No input detected, using default of 20")
            break
        
        try:
            intInput = int(userInput)
            threshold = intInput
            break
        except ValueError:
            print("Please only user valid integers (ie: '20'), try again.")
            
    return threshold


def generate_73_sr_data(pl1pl2: dict, tl6: dict) -> int:
    """
    Generates the subsystem 7.3 shift register data byte.
    we need pl1/2 data as the flash reset bit does not fit into the 7.2 byte.
    
    Parameters:
        pl1pl2 (dict): PL1 and PL2 (in sync) traffic light data
        tl6 (dict): TL6 traffic light data
    Returns:
        data (byte): byte representing the data to send to the 7.3 shift register
    """
    data = 0b0000_0000
    
    # BIT MAP:
    # X000_0000 PL1/2 flash enable (555 reset)
    # 0X00_0000 TL6 flash enable (555 reset)
    # 00X0_0000 TL6 green
    # 000X_0000 TL6 yellow
    # 0000_X000 TL6 red
    # 0000_0X00 NC
    # 0000_00X0 NC
    # 0000_000X NC
    
    if pl1pl2["state"] == lightState["FLASHING"]:
        data |= 0b1000_0000 # 555 reset HIGH (enable flashing)

    if tl6["state"] == lightState["FLASHING"]:
        data |= 0b0100_0000 # TL6 reset HIGH (enable flashing)

    if tl6["state"] == lightState["GREEN"]:
        data |= 0b0010_0000 
    elif tl6["state"] == lightState["YELLOW"]:
        data |= 0b0001_0000 
    elif tl6["state"] == lightState["RED"]:
        data |= 0b0000_1000 
        
    return data