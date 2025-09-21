from pymata4 import pymata4
import time 

from helpers import *

# shift register pins
SER = 4
RCLK = 8
SRCLK = 9

# button input pins
PB1_PB2 = 13

board = pymata4.Pymata4()


def pedestrian_handle_idle(pedCrossingStateMachine: dict, elapsedTime: float, currentTime: float) -> None:
    """
    Idle state; simply exists to wait for the sequence to be started.
    
    Parameters:
        pedCrossingStateMachine (dict): The dictionary containing the state machine's variables.
        elapsedTime (float): The time passed in the current state in seconds.
        currentTime (float): The current time in seconds.
        
    Returns:
        None
    """
    pass


def pedestrian_handle_waiting_to_start(pedCrossingStateMachine: dict, elapsedTime: float, currentTime: float) -> None:
    """
    After waiting for two seconds at this state, this will determine which of TL4/5 needs to turn yellow, and update to that state.
    
    Parameters:
        pedCrossingStateMachine (dict): The dictionary containing the state machine's variables.
        elapsedTime (float): The time passed in the current state in seconds.
        currentTime (float): The current time in seconds.
        
    Returns:
        None
    """
    if elapsedTime >= pedCrossingStateMachine['waitDuration']:
        if pedCrossingStateMachine['tl5']['state'] != lightState["RED"]:
            set_tl_state(pedCrossingStateMachine['tl5'], lightState["YELLOW"])
            
            pedCrossingStateMachine['state'] = 'tl5Yellow'
        else:
            set_tl_state(pedCrossingStateMachine['tl4'], lightState["YELLOW"])
            
            pedCrossingStateMachine['state'] = 'tl4Yellow'
        
        pedCrossingStateMachine['stateTimeStarted'] = currentTime


def pedestrian_handle_tl5_yellow(pedCrossingStateMachine: dict, elapsedTime: float, currentTime: float) -> None:
    """
    After waiting three seconds at this state, TL5 goes red and the pedestrian crossing starts.
    
    Parameters:
        pedCrossingStateMachine (dict): The dictionary containing the state machine's variables.
        elapsedTime (float): The time passed in the current state in seconds.
        currentTime (float): The current time in seconds.
        
    Returns:
        None
    """
    if elapsedTime >= pedCrossingStateMachine['tlYellowDuration']:
        set_tl_state(pedCrossingStateMachine['tl5'], lightState["RED"])
        set_tl_state(pedCrossingStateMachine['pl1Pl2'], lightState["GREEN"])
        
        pedCrossingStateMachine['state'] = 'plGreen'
        pedCrossingStateMachine['stateTimeStarted'] = currentTime


def pedestrian_handle_tl4_yellow(pedCrossingStateMachine: dict, elapsedTime: float, currentTime: float) -> None:
    """
    After waiting three seconds at this state, TL4 goes red and the pedestrian crossing starts.
    
    Parameters:
        pedCrossingStateMachine (dict): The dictionary containing the state machine's variables.
        elapsedTime (float): The time passed in the current state in seconds.
        currentTime (float): The current time in seconds.
        
    Returns:
        None
    """
    if elapsedTime >= pedCrossingStateMachine['tlYellowDuration']:
        set_tl_state(pedCrossingStateMachine['tl4'], lightState["RED"])
        set_tl_state(pedCrossingStateMachine['pl1Pl2'], lightState["GREEN"])
        
        pedCrossingStateMachine['state'] = 'plGreen'
        pedCrossingStateMachine['stateTimeStarted'] = currentTime


def pedestrian_handle_pl_green(pedCrossingStateMachine: dict, elapsedTime: float, currentTime: float) -> None:
    """
    This state keeps PL1/2 green for 3 seconds, after which it sets them to flashing red.
    
    Parameters:
        pedCrossingStateMachine (dict): The dictionary containing the state machine's variables.
        elapsedTime (float): The time passed in the current state in seconds.
        currentTime (float): The current time in seconds.
        
    Returns:
        None
    """
    if elapsedTime >= pedCrossingStateMachine['plGreenDuration']:
        pedCrossingStateMachine['state'] = 'plFlashingRed'
        pedCrossingStateMachine['stateTimeStarted'] = currentTime


def pedestrian_handle_pl_flashing_red(pedCrossingStateMachine: dict, elapsedTime: float, currentTime: float) -> None:
    """
    The final state, keeps PL1/2 flashing red for 2s, after which it resets to the idle state.
    
    Parameters:
        pedCrossingStateMachine (dict): The dictionary containing the state machine's variables.
        elapsedTime (float): The time passed in the current state in seconds.
        currentTime (float): The current time in seconds.
        
    Returns:
        None
    """
    # Flashing is handled separately. This function only manages state transitions.
    if elapsedTime >= pedCrossingStateMachine['plFlashingRedDuration']:
        set_tl_state(pedCrossingStateMachine['pl1Pl2'], lightState["RED"])
        set_tl_state(pedCrossingStateMachine['tl4'], lightState["GREEN"])
        
        pedCrossingStateMachine['active'] = False
        pedCrossingStateMachine['state'] = 'idle'
        pedCrossingStateMachine['stateTimeStarted'] = 0 
        pedCrossingStateMachine['seqLastActiveTime'] = currentTime


def create_pedestrian_sm(tl4: dict, tl5: dict, pl1Pl2: dict) -> dict:
    """
    Initializes and returns a new state dictionary for the pedestrian crossing sequence statemachine
    
    Parameters:
        tl4 (dict): The traffic light 4 state dictionary.
        tl5 (dict): The traffic light 5 state dictionary.
        pl1Pl2 (dict): The pedestrian light 1/2 state dictionary.
        
    Returns:
        dict: A dictionary representing the entire pedestrian sequence state machine.
    """
    pedestrianStateHandlers = {
        'idle': pedestrian_handle_idle,
        'waitingToStart': pedestrian_handle_waiting_to_start,
        'tl5Yellow': pedestrian_handle_tl5_yellow,
        'tl4Yellow': pedestrian_handle_tl4_yellow,
        'plGreen': pedestrian_handle_pl_green,
        'plFlashingRed': pedestrian_handle_pl_flashing_red
    }

    return {
        'active': False,
        'state': 'idle',
        'stateTimeStarted': 0,
        'seqLastActiveTime': 0,
        'tl4': tl4,
        'tl5': tl5,
        'pl1Pl2': pl1Pl2,
        'waitDuration': 2,
        'tlYellowDuration': 3,
        'plGreenDuration': 3,
        'plFlashingRedDuration': 2,
        'pl1Pl2FlashPerSec': 5,
        'pedestrianStateHandlers': pedestrianStateHandlers
    }


def start_ped_crossing_sequence(pedCrossingStateMachine: dict) -> None:
    """
    Starts the pedestrian crossing sequence.
    
    Parameters:
        pedCrossingStateMachine (dict): The dictionary containing the state machine's variables.
        
    Returns:
        None
    """
    if not pedCrossingStateMachine['active']:
        print("Pedestrain button has been pressed, starting crossing sequence")
        pedCrossingStateMachine['active'] = True
        
        pedCrossingStateMachine['state'] = 'waitingToStart'
        pedCrossingStateMachine['stateTimeStarted'] = time.time()


def update_ped_crossing_sequence(pedCrossingStateMachine: dict) -> None:
    """
    Updates the current state of the pedestrian crossing.
    
    Parameters:
        pedCrossingStateMachine (dict): The dictionary containing the state machine's variables.
        
    Returns:
        None
    """
    if not pedCrossingStateMachine['active']:
        return
        
    currentTime = time.time()
    stateElapsedTime = currentTime - pedCrossingStateMachine['stateTimeStarted']

    # grab the handler that we need
    handler = pedCrossingStateMachine['pedestrianStateHandlers'][pedCrossingStateMachine['state']]
    if handler:
        handler(pedCrossingStateMachine, stateElapsedTime, currentTime)


def setup() -> None:
    """
    pin setup / default pin states
    
    Parameters: 
        None
    
    Returns:
        None
    """
    #shift register pins
    board.set_pin_mode_digital_output(SER)
    board.set_pin_mode_digital_output(RCLK)
    board.set_pin_mode_digital_output(SRCLK)
    
    # flush
    update_shift_register(board, SER, SRCLK, RCLK, 0b0000_0000)
    
    # button pins:
    board.set_pin_mode_digital_input(PB1_PB2)


def update_tl4_tl5_pl1_pl2(tl4: dict, tl5: dict, pl1_pl2: dict) -> None:
    """
    packages the tl4, tl5, pl1/2 traffic light data into a byte that is sent onto their shift register for hardware communication
    
    Parameters:
        tl4 (TrafficLight): TL4 traffic light data
        tl5 (TrafficLight): TL5 traffic light data
        pl1_pl2 (TrafficLight): PL1 and PL2 (in sync) traffic light data 
        
    Returns:
        None
    """
    data = 0b0000_0000
    
    # bits and what the match to (MSB to LSB)
    # X000_0000 PL1/2 green
    # 0X00_0000 PL1/2 red
    # 00X0_0000 TL4 yelloW
    # 000X_0000 TL5 yelloW
    # 0000_X000 TL4 red
    # 0000_0X00 TL5 red
    # 0000_00X0 TL4 green
    # 0000_000X TL5 green
    
    
    # mask tl4 data
    if tl4["state"] == lightState["GREEN"]:
        data |= 0b0000_0010
    elif tl4["state"] == lightState["RED"]:
        data |= 0b0000_1000
    elif tl4["state"] == lightState["YELLOW"]:
        data |= 0b0010_0000
        
    # mask tl5 data
    if tl5["state"] == lightState["GREEN"]:
        data |= 0b0000_0001
    elif tl5["state"] == lightState["RED"]:
        data |= 0b0000_0100
    elif tl5["state"] == lightState["YELLOW"]:
        data |= 0b0001_0000
        
    # mask pl1/pl2 data
    if pl1_pl2["state"] == lightState["GREEN"]:
        data |= 0b1000_0000
    elif pl1_pl2["state"] == lightState["RED"]:
        data |= 0b0100_0000
    elif pl1_pl2["state"] == lightState["OFF"]:
        data &= 0b0011_1111 # keep every bit but not for pl1/2
        
    update_shift_register(board, SER, SRCLK, RCLK, data)
 

def main():
    """
    Main logic loop of the traffic light system
    
    Parameters:
        None
        
    Returns: 
        None
    """
    setup()
    
    # create the lights for subsystem 7.2 and send to the register
    # tl4 = TrafficLight("TL4", lightState["GREEN"])
    tl4 = create_traffic_light("TL4", lightState["GREEN"])
    
    tl4GreenDuration = 20
    tl4YellowDuration = 3
    
    # tl5 = TrafficLight("TL5", lightState["RED"])
    tl5 = create_traffic_light("TL5", lightState["RED"])
    tl5GreenDuration = 10
    tl5YellowDuration = 3
    
    # pl1Pl2 = TrafficLight("PL1_PL2", lightState["RED"])
    pl1Pl2 = create_traffic_light("PL1 PL2", lightState["RED"])
    
    update_tl4_tl5_pl1_pl2(tl4, tl5, pl1Pl2)
    
    # pedestrianCrossing = PedestrianSequence(tl4, tl5, pl1Pl2)
    pedestrianCrossing = create_pedestrian_sm(tl4, tl5, pl1Pl2)
    
    while True:
        try:
            # check if the crossing sequence has been activated 
            if not pedestrianCrossing["active"] and board.digital_read(PB1_PB2)[0] == HIGH:
                start_ped_crossing_sequence(pedestrianCrossing)
            
            
            if pedestrianCrossing["active"]:
                update_ped_crossing_sequence(pedestrianCrossing)
            else:
                # TL4 state updating
                if tl4["state"] == lightState["GREEN"] and tl_state_elapsed_time(tl4) > tl4GreenDuration:
                    # TL4 green to yellow
                    # tl4.set_state(lightState["YELLOW"])
                    set_tl_state(tl4, lightState["YELLOW"])
                    
                elif tl4["state"] == lightState["YELLOW"] and tl_state_elapsed_time(tl4) > tl4YellowDuration:
                    # TL4 yellow to red
                    # tl4.set_state(lightState["RED"])
                    set_tl_state(tl4, lightState["RED"])
                
                    # when TL4 turns red, TL5 turns green
                    # tl5.set_state(lightState["GREEN"])
                    set_tl_state(tl5, lightState["GREEN"])
                

                # TL5 state updating
                if tl5["state"] == lightState["GREEN"] and tl_state_elapsed_time(tl5) > tl5GreenDuration:
                    # TL4 green to yellow
                    # tl5.set_state(lightState["YELLOW"])
                    set_tl_state(tl5, lightState["YELLOW"])

                    
                elif tl5["state"] == lightState["YELLOW"] and tl_state_elapsed_time(tl5) > tl5YellowDuration:
                    # TL4 yellow to red
                    # tl5.set_state(lightState["RED"])
                    set_tl_state(tl5, lightState["RED"])
                
                    # when TL4 turns red, TL5 turns green
                    # tl4.set_state(lightState["GREEN"])
                    set_tl_state(tl4, lightState["GREEN"])

        except KeyboardInterrupt:
            return
        
        update_tl4_tl5_pl1_pl2(tl4, tl5, pl1Pl2)
        # minor sleep to not eat up cpu
        time.sleep(0.05)
        
    
    
    
if __name__ == "__main__":
    main()
    board.shutdown()