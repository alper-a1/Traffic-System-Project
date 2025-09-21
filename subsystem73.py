from pymata4 import pymata4
import time

from helpers import *

board = pymata4.Pymata4()

us5trig = 2
us5echo = 3

tl6green = 10
tl6yellow = 11
tl6red = 12

def setup() -> None:
    """
    pin setup / default pin states
    
    Parameters: 
        None
    
    Returns:
        None
    """
    #shift register pins
    board.set_pin_mode_digital_output(tl6green)
    board.set_pin_mode_digital_output(tl6red)
    board.set_pin_mode_digital_output(tl6yellow)
    
    board.set_pin_mode_sonar(us5trig, us5echo, us5_sonar_callback, timeout=200000)


def us5_sonar_callback(data):
    """
    callback function for US5, exists for debugging.
    """
    if DEBUG:
        print("US5: ", data)

'''
class VehicleExit:
    """
    State machine to handle the overheight vehicle exit sequence.
    """
    
    def __init__(self, tl6: TrafficLight, overheightLimit: int) -> None:
        self.tl6 = tl6
        self.overheightLimit = overheightLimit
        self.tl6YellowDurationSec = 3
        self.tl6MinGreenDurationSec = 5
        
        self.active = False
        
        self.state = 'idle' 
        self.stateTimeStarted = 0
        
        # The dispatch table (lookup dictionary)
        self.stateHandlers = {
            'idle': self._handle_idle,
            'green': self._handle_green,
            'yellow': self._handle_yellow
        }

    def start(self) -> None:
        if not self.active:
            self.active = True
            self.tl6.set_state(lightState["GREEN"])
            
            self.state = 'green' 
            self.stateTimeStarted = time.time()

    def update_sequence(self, us5data: int) -> None:
        """
        Run and or update the current state if active.
        
        Parameters:
            us5data (int): distance read (in cm) from US5
            
        Returns:
            None
        """
        if not self.active:
            return
        
        currentTime = time.time()
        elapsedTime = currentTime - self.stateTimeStarted

        # get the handler for the current state from the dispatch table
        handler = self.stateHandlers.get(self.state)
        if handler:
            handler(elapsedTime, us5data)

    def _handle_idle(self, elapsedTime: float, us5data: int) -> None:
        """
        Idle state; since VehicleExit has no action for being idle other than waiting to start, this state simply exists for readability / debug
        
        Parameters:
            elapsedTtime (float): seconds elapsed in the current state
            us5data (int): distance read (in cm) from US5
           
        Returns:
            None 
        """
        pass

    def _handle_green(self, elapsedTime: float, us5data: int) -> None:
        """
        handler for the green state, the exit sequence stays on this state for at least 5 seconds, 
        after which it will only proceed if there is no longer an overheight detection
        
        Parameters:
            elapsedTtime (float): seconds elapsed in the current state
            us5data (int): distance read (in cm) from US5
           
        Returns:
            None 
        """
        if elapsedTime >= self.tl6MinGreenDurationSec and us5data <= self.overheightLimit:
            self.tl6.set_state(lightState["YELLOW"])
            
            self.state = 'yellow'  
            self.stateTimeStarted = time.time()
            
    def _handle_yellow(self, elapsedTime: float, us5data: int) -> None:
        """
        intermediate state holding tl6 for the desired time in seconds until returning back to idle
        
        Parameters:
            elapsedTtime (float): seconds elapsed in the current state
            us5data (int): distance read (in cm) from US5
           
        Returns:
            None  
        """
        if elapsedTime >= self.tl6YellowDurationSec:
            self.tl6.set_state(lightState["RED"])
            
            self.active = False
            self.state = 'idle'  
'''

import time

# Assumed global functions and variables from elsewhere in your code:
# - set_tl_state(traffic_light: dict, newState: int) -> None
# - lightState: a dictionary with light states, e.g., {"GREEN": 3, "RED": 1}

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

def vehicle_exit_handle_green(vehicleExitStateMachine: dict, elapsedTime: float, us5data: int) -> None:
    """
    Handler for the green state. The exit sequence stays on this state for at least 5 seconds, 
    after which it will only proceed if there is no longer an overheight detection.
    
    Parameters:
        vehicleExitStateMachine (dict): The dictionary containing the state machine's variables.
        elapsedTime (float): seconds elapsed in the current state.
        us5data (int): distance read (in cm) from US5.
            
    Returns:
        None 
    """
    if elapsedTime >= vehicleExitStateMachine['tl6MinGreenDurationSec'] and us5data <= vehicleExitStateMachine['overheightLimit']:
        set_tl_state(vehicleExitStateMachine['tl6'], lightState["YELLOW"])
        
        vehicleExitStateMachine['state'] = 'yellow'  
        vehicleExitStateMachine['stateTimeStarted'] = time.time()
        
def vehicle_exit_handle_yellow(vehicleExitStateMachine: dict, elapsedTime: float, us5data: int) -> None:
    """
    Intermediate state holding tl6 for the desired time in seconds until returning back to idle.
    
    Parameters:
        vehicleExitStateMachine (dict): The dictionary containing the state machine's variables.
        elapsedTime (float): seconds elapsed in the current state.
        us5data (int): distance read (in cm) from US5.
            
    Returns:
        None  
    """
    if elapsedTime >= vehicleExitStateMachine['tl6YellowDurationSec']:
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
        'green': vehicle_exit_handle_green,
        'yellow': vehicle_exit_handle_yellow
    }

    return {
        'tl6': tl6,
        'overheightLimit': overheightLimit,
        'tl6YellowDurationSec': 3,
        'tl6MinGreenDurationSec': 5,
        'active': False,
        'state': 'idle', 
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
        set_tl_state(vehicleExitStateMachine['tl6'], lightState["GREEN"])
        
        vehicleExitStateMachine['state'] = 'green' 
        vehicleExitStateMachine['stateTimeStarted'] = time.time()


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
    handler = vehicleExitStateMachine['vehicleExitStateHandlers'].get(vehicleExitStateMachine['state'])
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


def main():
    """
    Main logic loop of subsystem 7.2
    
    Parameters:
        None
        
    Returns: 
        None
    """
    setup()
    
    threshold = get_user_overheight_threshold()
    
    # tl6 = TrafficLight("TL6", lightState["RED"])
    tl6 = create_traffic_light("TL6", lightState["RED"])
    # exitSequence = VehicleExit(tl6, threshold)
    vehicleExitSM = create_vehicle_exit(tl6, threshold)
    
    while True:
        try:
            us5data = board.sonar_read(us5trig)[0]
            if us5data > threshold:
                # exitSequence.start()
                start_vehicle_exit(vehicleExitSM)
                
            # exitSequence.update_sequence(us5data)  
            update_vehicle_exit_sequence(vehicleExitSM, us5data)     
            
            if tl6["state"] == lightState["GREEN"]:
                board.digital_write(tl6green, HIGH)
                board.digital_write(tl6red, LOW)
                board.digital_write(tl6yellow, LOW)
            elif tl6["state"] == lightState["YELLOW"]:
                board.digital_write(tl6green, LOW)
                board.digital_write(tl6red, LOW)
                board.digital_write(tl6yellow, HIGH)
            elif tl6["state"] == lightState["RED"]:
                board.digital_write(tl6green, LOW)
                board.digital_write(tl6red, HIGH)
                board.digital_write(tl6yellow, LOW) 
        except KeyboardInterrupt:
            return
        

        time.sleep(0.1)
        
    
if __name__ == "__main__":
    main()
    board.shutdown()