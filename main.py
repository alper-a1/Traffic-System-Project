# main.py
# Author: F24 team
# Created Date: 02/10/2025
# Last Changed: 2025-10-02
# Version ='0.02'

from pymata4 import pymata4
import time 

from helpers import *

from subsystem72 import *
from subsystem73 import *


board = pymata4.Pymata4()

# PIN DEFINITIONS
serialPin = 4
rclkPin = 8
srclkPin = 9
us5TrigPin = 12
us5EchoPin = 13
pb1pb2Pin = 2


def update_registers(data72reg: int, data73reg: int) -> None:
    """
    updates both shift registers with new data.
    
    Parameters:
        data72reg (byte): data for the 7.2 shift register
        data73reg (byte): data for the 7.3 shift register
        
    Returns:
        None
    """
    def send_byte(byte: int) -> None:
        """
        sends a byte through serial, LSB first
        
        Parameters:
            byte (byte): the byte to send
    
        Returns:
            None
        """
        for _ in range(8):
            # isolate the LSB
            bit = byte & 0b0000_0001
            
            # write the bit to the serial pin
            board.digital_write(serialPin, bit)
            
            # pulse the serial clock to indicate that a bit is ready
            board.digital_write(srclkPin, HIGH)
            board.digital_write(srclkPin, LOW)
            
            # shift the byte right by one to get the next bit
            byte >>= 1
    
    # update 7.3 first, as it is "behind" 7.2 in the daisy chain
    board.digital_write(rclkPin, LOW) 
    
    send_byte(data73reg)
    send_byte(data72reg)

    board.digital_write(rclkPin, HIGH) 

def setup() -> None:
    """
    inital arduino setup, runs once before main loop starts. 
    do pin setup / default pin states here
    
    Parameters: 
        None
    
    Returns:
        None
    """
    #shift register pins
    board.set_pin_mode_digital_output(serialPin)
    board.set_pin_mode_digital_output(rclkPin)
    board.set_pin_mode_digital_output(srclkPin)
    
    # flush
    update_registers(0b0000_0000, 0b0000_0000)
    
    # button pins:
    board.set_pin_mode_digital_input(pb1pb2Pin)
    
    # ultrasonic pins
    board.set_pin_mode_sonar(us5TrigPin, us5EchoPin, us5_sonar_callback, timeout=200000)



def main():
    """
    Main logic loop of the traffic light system
    
    Parameters:
        None
        
    Returns: 
        None
    """
    setup()
    
    
    # system wide overheight threshold
    threshold = get_user_overheight_threshold()
    
  
    
    
    # 7.2 initalisation
    tl4 = create_traffic_light("TL4", lightState["GREEN"])
    
    tl4GreenDuration = 20
    tl4YellowDuration = 3
    
    tl5 = create_traffic_light("TL5", lightState["RED"])
    tl5GreenDuration = 10
    tl5YellowDuration = 3
    
    pl1Pl2 = create_traffic_light("PL1 PL2", lightState["RED"])

    data72 = generate_72_sr_data(tl4, tl5, pl1Pl2)

    pedestrianCrossing = create_pedestrian_sm(tl4, tl5, pl1Pl2)
    
    # 7.3 initalisation
    tl6 = create_traffic_light("TL6", lightState["RED"])
    vehicleExitSM = create_vehicle_exit(tl6, threshold)

    data73 = generate_73_sr_data(pl1Pl2, tl6)




    update_registers(data72, data73)

    # main loop
    while True:
        try:
            # 7.3 logic
            us5data = board.sonar_read(us5TrigPin)[0]
            if us5data > threshold:
                start_vehicle_exit(vehicleExitSM)
                    
            update_vehicle_exit_sequence(vehicleExitSM, us5data)     
                
            # 7.2 logic
            # check if the crossing sequence has been activated 
            if not pedestrianCrossing["active"] and board.digital_read(pb1pb2Pin)[0] == HIGH:
                start_ped_crossing_sequence(pedestrianCrossing)
            
            
            if pedestrianCrossing["active"]:
                update_ped_crossing_sequence(pedestrianCrossing)
            else:
                # TL4 state updating
                if tl4["state"] == lightState["GREEN"] and tl_state_elapsed_time(tl4) > tl4GreenDuration:
                    # TL4 green to yellow
                    set_tl_state(tl4, lightState["YELLOW"])
                    
                elif tl4["state"] == lightState["YELLOW"] and tl_state_elapsed_time(tl4) > tl4YellowDuration:
                    # TL4 yellow to red
                    set_tl_state(tl4, lightState["RED"])
                
                    # when TL4 turns red, TL5 turns green
                    set_tl_state(tl5, lightState["GREEN"])
                

                # TL5 state updating
                if tl5["state"] == lightState["GREEN"] and tl_state_elapsed_time(tl5) > tl5GreenDuration:
                    # TL4 green to yellow
                    set_tl_state(tl5, lightState["YELLOW"])

                    
                elif tl5["state"] == lightState["YELLOW"] and tl_state_elapsed_time(tl5) > tl5YellowDuration:
                    # TL4 yellow to red
                    set_tl_state(tl5, lightState["RED"])
                
                    # when TL4 turns red, TL5 turns green
                    set_tl_state(tl4, lightState["GREEN"])

        except KeyboardInterrupt:
            return
        
        data72 = generate_72_sr_data(tl4, tl5, pl1Pl2)
        data73 = generate_73_sr_data(pl1Pl2, tl6)
        
        update_registers(data72, data73)
        
        # minor sleep to not eat up cpu
        time.sleep(0.05)
        
    
    
    
if __name__ == "__main__":
    main()
    board.shutdown()