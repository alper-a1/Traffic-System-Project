# main.py
# Author: F24 team
# Created Date: 02/10/2025
# Last Changed: 2025-10-11
# Version ='0.03'

from pymata4 import pymata4
import time 

from helpers import *

from subsystem71 import *
from subsystem72 import *
from subsystem73 import *


board = pymata4.Pymata4()

# PIN DEFINITIONS
serialPin = 10
rclkPin = 8
srclkPin = 9

pb1pb2Pin = 13


us1EchoPin = 3
us1TrigPin = 2

us2EchoPin = 5
us2TrigPin = 4

us5TrigPin = 6
us5EchoPin = 7

def update_registers(data71reg: int, data72reg: int, data73reg: int) -> None:
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
            board.digital_write(srclkPin, high)
            # small sleep is otherwise python speed means the pins flip too high 
            time.sleep(0.001)
            board.digital_write(srclkPin, low)
            
            # shift the byte right by one to get the next bit
            byte >>= 1 
    
    # update 7.3 first, as it is "behind" 7.2 in the daisy chain
    board.digital_write(rclkPin, low) 
    
    send_byte(data71reg)
    send_byte(data73reg)
    send_byte(data72reg)

    board.digital_write(rclkPin, high) 

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
    update_registers(0b0000_0000, 0b0000_0000, 0b0000_0000)
    
    # button pins:
    board.set_pin_mode_digital_input(pb1pb2Pin)
    
    # ultrasonic pins
    board.set_pin_mode_sonar(us5TrigPin, us5EchoPin, us5_sonar_callback, timeout=200000)

    board.set_pin_mode_sonar(us1TrigPin, us1EchoPin, timeout=200000, callback=us1_callback)
    board.set_pin_mode_sonar(us2TrigPin, us2EchoPin, timeout=200000, callback=us2_callback)



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
    # threshold = get_user_overheight_threshold()
    overHeightThreshold =  15
  
    
    # 7.2 initalisation
    tl4 = create_traffic_light("TL4", lightState["GREEN"])
    
    tl4GreenDuration = 20
    tl4YellowDuration = 3
    
    tl5 = create_traffic_light("TL5", lightState["RED"])
    tl5GreenDuration = 10
    tl5YellowDuration = 3
    
    pl1Pl2 = create_traffic_light("PL1 PL2", lightState["RED"])

    data72 = generate_72_sr_data(tl4, tl5, pl1Pl2)

    pedestrianCrossing = create_pedestrian_sm(tl4, tl5, pl1Pl2, overHeightThreshold)
    
    # 7.3 initalisation
    tl6 = create_traffic_light("TL6", lightState["RED"])
    vehicleExitSM = create_vehicle_exit(tl6, overHeightThreshold)

    data73 = generate_73_sr_data(pl1Pl2, tl6)


    # 7.1 initalisation
    data71 = generate_71_sr_data(tl1State[0],tl2State[0],pa1State[0])
    us2Tl1Override = False
    tl2Only = False
    tl1Process = False

    update_registers(data71, data72, data73)

    # main loop
    while True:
        try:
            # 7.3 logic
            us5data = board.sonar_read(us5TrigPin)[0]
            if us5data <= overHeightThreshold:
                start_vehicle_exit(vehicleExitSM)
                    
            update_vehicle_exit_sequence(vehicleExitSM, us5data)     
            
            # 7.2 & 7.3 integration 2.I1 (and 3.I1)
            
            # if we detect an overheight we start the crossing sequence skipping the 2 second wait.
            if us5data <= overHeightThreshold:
                start_ped_crossing_sequence(pedestrianCrossing, True)
                
            # 7.2 logic
            # check if the crossing sequence has been activated 
            if not pedestrianCrossing["active"] and board.digital_read(pb1pb2Pin)[0] == high:
                start_ped_crossing_sequence(pedestrianCrossing)
            
            
            if pedestrianCrossing["active"]:
                update_ped_crossing_sequence(pedestrianCrossing, us5data)
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

        # ---------
            
            # check if us2 has detected an ovreheight vehicle
            if us2OverHeight[0] or tl2State[0] != "green":
                # check if us1 has recently detected the vehicle or currently running tl2Only branch
                if (us1OverHeight[0] or ((time.time() - us1OverHeight[1]) <= us1ToUs2Timing)  or (tl1Process)):
                    tl2Only = True
                elif tl2Only:
                    tl2Only = True
                else:
                    tl2Only = False
                # if us1 has detected a vehicle run the tl2Only branch
                if tl2Only and (not us2Tl1Override):
                    if tl2State[0] == "green":
                        tl2State[0] = "yellow"
                        tl2State[1] = time.time()
                    elif tl2State[0] == "yellow" and time.time() - tl2State[1] > tl12YellowLightTime:
                        tl2State[0] = "red"
                        tl2State[1] = time.time()
                    elif tl2State[0] == "red" and time.time() - tl2State[1] > tl12RedLightTime:
                        # if after red time is over and overheight still deteteced stay red
                        if not us2OverHeight[0]:
                            tl2State[0] = "green"
                            tl2State[1] = time.time()
                            # once done set tl2Only to false to say show the tl2Only branch is done running
                            tl2Only = False
                # if us1 has not detected the vehicle then the override branch to change both traffic lights
                else:
                    us2Tl1Override = True
                    if tl2State[0] == "green":
                        tl1State[0] = "yellow"
                        tl2State[0] = "yellow"
                        tl1State[1] = time.time()
                        tl2State[1] = time.time()
                    elif (tl2State[0] == "yellow") and ((time.time() - tl2State[1]) > tl12YellowLightTime):
                        tl1State[0] = "red"
                        tl2State[0] = "red"
                        subsystem71Data = (generate_71_sr_data(tl1State[0],tl2State[0],pa1State[0]))
                        tl1State[1] = time.time()
                        tl2State[1] = time.time()
                    elif (tl2State[0] == "red") and ((time.time() - tl2State[1]) > tl12RedLightTime):
                        # if after red time is over and overheight still deteteced stay red
                        if not us2OverHeight[0]:
                            tl1State[0] = "green"
                            tl2State[0] = "green"
                            tl1State[1] = time.time()
                            tl2State[1] = time.time()
                            # turn off override once the procedure is complete
                            us2Tl1Override = False

            # us1 over height detection and tl1 control
            if (not us2Tl1Override) and (us1OverHeight[0]) and (tl1State[0] == "green"):
                tl1Process = True
                print(f"Over Height Vehicle Detected, Height: {overHeight/10}m, Date & Time: {time.ctime()}")
                tl1State[0] = "yellow" 
                tl1State[1] = time.time()
            elif (not us2Tl1Override) and tl1State[0] == "yellow" and time.time() - tl1State[1] > tl12YellowLightTime:
                tl1State[0] = "red" 
                tl1State[1] = time.time()
            elif (not us2Tl1Override) and tl1State[0] == "red" and time.time() - tl1State[1] > tl12RedLightTime:
                # if after red time is over and overheight still deteteced stay red
                if not us1OverHeight[0]:
                    tl1State[0] = "green"
                    tl1State[1] = time.time()
                    tl1Process = False

            # # pa1 siren
            if tl1State[0] == 'red' and (time.time() - tl1State[1] > tl12RedLightTime):
                pa1State[0] = 'high'
                pa1State[1] = time.time() 
            elif tl1State[0] != 'green':
                pa1State[0] = 'low'
                pa1State[1] = time.time() 
            else:
                pa1State[0] = 'off'
                pa1State[1] = time.time() 


        except KeyboardInterrupt:
            return
        
        data71 = generate_71_sr_data(tl1State[0],tl2State[0],pa1State[0])
        data72 = generate_72_sr_data(tl4, tl5, pl1Pl2)
        data73 = generate_73_sr_data(pl1Pl2, tl6)
        
        
        
        update_registers(data71, data72, data73)
        
        # minor sleep to not eat up cpu
        time.sleep(0.05)
        
    
    
    
if __name__ == "__main__":
    main()
    board.shutdown()