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


class PedestrianSequence():
    """
    Handler for the pedestrian crossing with PL1/2 and TL4/5

    sequence states are as follows:
    0: wait 2s -> choose which TL to make yellow (jump to state 1/2)
    
    STATE 1 & 2 are NOT sequential - they are both branches off 0
    1: if tl5 not red, tl5 yellow for 3s, then red -> PL1/2 green
    2: tl4 yellow, then red -> PL1/2 green
    
    3: ped lights green for 3s -> PL1/2 FLASHING RED
    4: 2s PL1/2 FLASHING RED -> reset sequence; PL1/2 RED, TL4 green    
    """
    
    def __init__(self, tl4: dict, tl5: dict, pl1Pl2: dict) -> None:
        self.active = False
        self.state = 'idle'
        self.stateTimeStarted = 0
        
        self.seqLastActiveTime = 0 # variable for future 2.G1 implementation
        
        self.tl4 = tl4
        self.tl5 = tl5
        self.pl1Pl2 = pl1Pl2
        
        # all times are in seconds
        self.waitDuration = 2
        self.tlYellowDuration = 3
        self.plGreenDuration = 3
        self.plFlashingRedDuration = 2
        
        self.pl1Pl2FlashPerSec = 5

        # handlers for each state
        self.state_handlers = {
            'idle': self._handle_idle,
            'waiting_to_start': self._handle_waiting_to_start,
            'tl5_yellow': self._handle_tl5_yellow,
            'tl4_yellow': self._handle_tl4_yellow,
            'pl_green': self._handle_pl_green,
            'pl_flashing_red': self._handle_pl_flashing_red
        }
        
    def start(self) -> None:
        """
        Start the crossing sequence (stops the current TL4/5 cycle)
        
        Parameters:
            None
            
        Returns:
            None
        """
        if not self.active:
            print("Pedestrain button has been pressed, starting crossing sequence")
            self.active = True
            
            self.state = 'waiting_to_start'
            self.stateTimeStarted = time.time()
            
    def update_sequence(self) -> None:
        """
        update the current state of the pedestrain crossing 
        
        Parameters:
            None
            
        Returns:
            None
        """
        if not self.active:
            return
            
        currentTime = time.time()
        stateElapsedTime = currentTime - self.stateTimeStarted

        handler = self.state_handlers.get(self.state)
        if handler:
            handler(stateElapsedTime, currentTime)

    def _handle_idle(self, elapsedTime, currentTime):
        """
        Idle state; since PedestrainCrossing has no action to take when idle other than wait for PB1/2 to be pressed, this simply exists for
        readability / debug
        
        Parameters:
            elapsedTime (float): time passed in the current state in seconds
            currentTime (float): current time in seconds
        
        Returns:
            None
        """
        pass

    def _handle_waiting_to_start(self, elapsedTime, currentTime):
        """
        After waiting for two seconds at this state, this will determine which of TL4/5 needs to turn yellow, and update to that state
        
        Parameters:
            elapsedTime (float): time passed in the current state in seconds
            currentTime (float): current time in seconds
        
        Returns:
            None
        """
        if elapsedTime >= self.waitDuration:
            if self.tl5["state"] != lightState["RED"]:
                set_tl_state(self.tl5, lightState["YELLOW"])
                
                self.state = 'tl5_yellow'
            else:
                set_tl_state(self.tl4, lightState["YELLOW"])
                
                self.state = 'tl4_yellow'
            
            self.stateTimeStarted = currentTime

    def _handle_tl5_yellow(self, elapsedTime, currentTime):
        """
        after waiting three seconds at this state, TL5 goes red and the pedestrian crossing starts (state 3)
        
        Parameters:
            elapsedTime (float): time passed in the current state in seconds
            currentTime (float): current time in seconds
        
        Returns:
            None
        """
        if elapsedTime >= self.tlYellowDuration:
            set_tl_state(self.tl5, lightState["RED"])

            set_tl_state(self.pl1Pl2, lightState["GREEN"])
            
            self.state = 'pl_green'
            self.stateTimeStarted = currentTime

    def _handle_tl4_yellow(self, elapsedTime, currentTime):
        """
        after waiting three seconds at this state, TL4 goes red and the pedestrian crossing starts (state 3)
        
        Parameters:
            elapsedTime (float): time passed in the current state in seconds
            currentTime (float): current time in seconds
        
        Returns:
            None
        """
        if elapsedTime >= self.tlYellowDuration:
            set_tl_state(self.tl4, lightState["RED"])
            
            set_tl_state(self.pl1Pl2, lightState["GREEN"])
            
            self.state = 'pl_green'
            self.stateTimeStarted = currentTime

    def _handle_pl_green(self, elapsedTime, currentTime):
        """
        this state keeps PL1/2 green for 3 seconds, after which it sets them to flashing red and jumps to state 4
        
        Parameters:
            elapsedTime (float): time passed in the current state in seconds
            currentTime (float): current time in seconds
        
        Returns:
            None
        """
        if elapsedTime >= self.plGreenDuration:
            
            self.state = 'pl_flashing_red'
            self.stateTimeStarted = currentTime

    def _handle_pl_flashing_red(self, elapsedTime, currentTime):
        """
        the final state, keeps PL1/2 flashing red for 2s, after which it resets to state 0 and sets the crossing sequence to inactive (resume TL4/5 cycle) 
        
        Parameters:
            elapsedTime (float): time passed in the current state in seconds
            currentTime (float): current time in seconds
        
        Returns:
            None
        """
        # flashing will be changed into hardware -- this is obsolete for now
        # self.pl1Pl2.flash_color(lightState["RED"], elapsedTime, self.pl1Pl2FlashPerSec)
        
        if elapsedTime >= self.plFlashingRedDuration:
            set_tl_state(self.pl1Pl2, lightState["RED"])
            
            set_tl_state(self.tl4, lightState["GREEN"])
            self.active = False
            self.state = 'idle'
            self.stateTimeStarted = 0 
            
            self.seqLastActiveTime = currentTime


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
    
    pedestrianCrossing = PedestrianSequence(tl4, tl5, pl1Pl2)
    
    while True:
        try:
            # check if the crossing sequence has been activated 
            if not pedestrianCrossing.active and board.digital_read(PB1_PB2)[0] == HIGH:
                pedestrianCrossing.start()
            
            
            if pedestrianCrossing.active:
                pedestrianCrossing.update_sequence()
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