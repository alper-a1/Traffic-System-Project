# Created By : Alper Alpcan
# Last Modified: 16/10/2025
# version = 0.4

# revision of original 7.4 code by Alper for integration

from helpers import *



def tunnel_detect_handle_normal(tunnelDetectionSM: dict, us1data: int, us2data: int, us3data: int, us4data: int, us5data: int) -> None:
    """
    This handles the idle state, where tl3 is green and no flashing
    to transition to warning state, us3 and us4 must be trigged simultaneously and with similar readings
    
    Parameters:
        tunnelDetectionStateMachine (dict): The dictionary containing the state machine's variables.
        us1data (int): distance read (in cm) from US1.
        us2data (int): distance read (in cm) from US2.
        us3data (int): distance read (in cm) from US3.
        us4data (int): distance read (in cm) from US4.
        us5data (int): distance read (in cm) from US5.
        
    Returns:
        None 
    """
    # TL3 is green and WL2 NOT flashing!
    set_tl_state(tunnelDetectionSM['tl3'], lightState['GREEN'])    
    set_tl_state(tunnelDetectionSM['wl2'], lightState['OFF'])    
    
    # if overheight has been detected:
    if us3data <= tunnelDetectionSM['overheightLimit']:
        
        # lets check if us4 agrees that there is an overheight
        error = abs(us3data - us4data) 
        
        # there is def an overheight vehicle, change state to overheight
        if error <= tunnelDetectionSM['errorTolerance']: 
            print(f"US3 and US4 have detected an overheight vehicle approaching with error: {error}, switching WL2 to warning state")
            tunnelDetectionSM['state'] = 'warning'
                

def tunnel_detect_handle_warning(tunnelDetectionSM: dict, us1data: int, us2data: int, us3data: int, us4data: int, us5data: int) -> None:
    """
    This handles the warning / flashing state when overheight is detected  
    transition back to normal only happens when all US1/2/3/4 are not detecting, and US5 detects overheight
    
    Parameters:
        tunnelDetectionStateMachine (dict): The dictionary containing the state machine's variables.
        us1data (int): distance read (in cm) from US1.
        us2data (int): distance read (in cm) from US2.
        us3data (int): distance read (in cm) from US3.
        us4data (int): distance read (in cm) from US4.
        us5data (int): distance read (in cm) from US5.
        
    Returns:
        None 
    """
    # TL3 is RED and WL2 flashing!
    set_tl_state(tunnelDetectionSM['tl3'], lightState['RED'])    
    set_tl_state(tunnelDetectionSM['wl2'], lightState['FLASHING'])    
    
    # we only go back to the normal state if US1/US2/US3/US4/US5 no longer detect an overheight vehicle
    # AND
    # US5 detects an overheight vehicle exiting
    us1To4Clear = ((us1data >= tunnelDetectionSM['overheightLimit']) and
                   (us2data >= tunnelDetectionSM['overheightLimit']) and 
                   (us3data >= tunnelDetectionSM['overheightLimit']) and 
                   (us4data >= tunnelDetectionSM['overheightLimit'])) 
    
    us5DetectedExit = us5data < tunnelDetectionSM['overheightLimit']

    if us1To4Clear and us5DetectedExit:
        tunnelDetectionSM['state'] = 'normal'
        


def create_tunnel_detection_sm(tl3: dict, wl2: dict, overheightLimit: int) -> dict:
    """
    Creates and initializes a tunnel detection state machine as a dictionary.
    
    Parameters:
        tl3 (dict): TL3 Traffic light reference
        wl2 (dict): WL2 Warning light reference
        overheightLimit (int): The height limit for detecting overheight vehicles.
    
    Returns:
        dict: A dictionary representing the tunnel detection state machine, containing:
            - 'tl3': The provided traffic light data.
            - 'wl2': The provided warning light data.
            - 'overheightLimit': The specified overheight limit.
            - 'errorTolerance': The error tolerance value (default is 5).
            - 'state': The initial state of the state machine ('normal').
            - 'tunnelDetectionStateHandlers': A mapping of state names to their handler functions.
    """
    tunnelDetectionStateHandlers = {
        'normal': tunnel_detect_handle_normal,
        'warning': tunnel_detect_handle_warning
    }
    
    # state machine with all instance variables. (cant use classes ;-;)
    # this can technically be a static dict and not runtime generated however its kept here for clarity
    return {
        'tl3': tl3,
        'wl2': wl2,
        'overheightLimit': overheightLimit,
        'errorTolerance': 5, 
        'state': 'normal', # intial state
        'tunnelDetectionStateHandlers': tunnelDetectionStateHandlers
    }
    

def update_tunnel_detection_sm(tunnelDetectionSM: dict, us1data: int, us2data: int, us3data: int, us4data: int, us5data: int) -> None:
    """
    Runs and/or updates the current state of tunnelDetectionStateMachine (always active)
    
    Parameters:
        tunnelDetectionStateMachine (dict): The dictionary containing the state machine's variables.
        us1data (int): distance read (in cm) from US1.
        us2data (int): distance read (in cm) from US2.
        us3data (int): distance read (in cm) from US3.
        us4data (int): distance read (in cm) from US4.
        us5data (int): distance read (in cm) from US5.
        
    Returns:
        None
    """
    # Get the handler for the current state from the dispatch table
    handler = tunnelDetectionSM['tunnelDetectionStateHandlers'][tunnelDetectionSM['state']]
    if handler:
        handler(tunnelDetectionSM, us1data, us2data, us3data, us4data, us5data)


def generate_74_sr_data(tl3: dict, wl2: dict) -> int:
    """
    Generates the subsystem 7.4 shift register data byte.
    
    Parameters:
        wl2 (dict): WL2 warning light data
        tl3 (dict): TL3 traffic light data
    Returns:
        data (byte): byte representing the data to send to the 7.3 shift register
    """
    data = 0b0000_0000
    
    # BIT MAP:
    # X000_0000 Tl3 red
    # 0X00_0000 WL2 flash enable (555 reset)
    # 00X0_0000 TL3 green
    # 000X_0000 NC
    # 0000_X000 NC
    # 0000_0X00 NC
    # 0000_00X0 NC
    # 0000_000X NC

    # OR in bits we need high
    if tl3['state'] == lightState["GREEN"]:
        data |= 0b0010_0000
        
    if tl3['state'] == lightState["RED"]:
        data |= 0b1000_0000
        
    if wl2['state'] == lightState["FLASHING"]:
        data |= 0b0100_0000

    return data

