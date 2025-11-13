# Arduino Road Traffic Control System
This was a major project completed in a group of 5 for one of my units at Monash University. It is intended to be a mock of a road traffic control system, using Pymata4 to facilitate arduino communications for ease of programming. Each 'Subsystem' has its own features, which are listed below in the [Subsystem Overview](https://github.com/alper-a1/Traffic-System-Project/new/main?filename=README.md#subsystem-overview) section further down.
The project achieved a 100% mark with all features implemented properly.
This project had a variety of limitations, most notably that python classes were prohibited, thus all state machines are dictionary based.
<figure>
  <img src="https://github.com/user-attachments/assets/c7b3b12d-1c36-489e-9480-626867b8ed4a" width="300">
  <figcaption></figcaption>
</figure>


# Overview of physical components
Circuit diagrams have been omitted from this repository, but a physical overview of the components is shown below. 
![IMG_20251023_162218917](https://github.com/user-attachments/assets/9667fd6a-0335-44d0-9854-f0df3110bf0e)

# Subsystem Overview
## Subsystem 1
**Features:**
1. Upon detection of an overheight vehicle by US1, an alert is printed to the console. The alert should include the detected height of the vehicle, as well as the date/time of detection.
2. Upon detection of an overheight vehicle by US1, the following sequence is triggered:
    1. TL1 switches to yellow for 1s, then to red for 30s.
    2. TL1 then turns back to green.
3. Upon detection of an overheight vehicle by US2, the following sequence is triggered:
    ●  If US1 did not detect an overheight vehicle, TL1 and TL2 immediately switch to yellow for 1s, then red for 30s before turning back to green.
    ● If US1 detected an overheight vehicle, then TL2 switches to yellow for 1s, then red for 30s before turning back to green.
4. Upon system start-up, the user is prompted to enter the overheight limit configuration for the system. If the user hits enter without providing any input, it defaults to the system default value of 4.0 meters. This value should be used as a variable in the entire subsystem.
5. Upon detection of an overheight vehicle by US1, PA1 turns on and begins sounding a unique buzzer tone (400Hz - 800Hz) so long as TL1 and TL2 are not green. The buzzer tone must be generated using a 555 timer.
6. Upon detection of an overheight vehicle by US1, TL1 and TL2 stays red if US1 continues to detect an overheight vehicle. After the initial 30s of red light duration, the buzzer tone on PA1 changes to a higher frequency tone. (tone must be between 2000Hz and 3000Hz higher) The buzzer tone must be generated using a 555 timer.
![IMG_20251023_162144405](https://github.com/user-attachments/assets/527ec0b3-7dd9-4e18-9db0-47f2aff932cf)

## Subsystem 2
**Features:**
1. If the pedestrian push button PB1/PB2 is pressed, the following sequence should be triggered after a two second wait. If TL5 is currently not red, TL5 goes yellow for 3s, then red. Otherwise, TL4 turns yellow for 3 seconds, then red.
    1. Then, PL1/PL2 turns green for 3s, then flashing red for 2s before resetting to solid red.
    2. Then, TL4 turns back to green.
2. If the pedestrian push button PB1/PB2 is pressed, show this information on the console once (until the sequence 2.R1 is run). (i.e. you should ensure that holding down or spamming the push button does not trigger multiple console prints).
3. TL4 and TL5 operate on a 20-10 second cycle. That is, after 20 seconds on green, TL4 will turn yellow (3s), then red. When TL4 turns red, TL5 turns green for 10 seconds, then yellow (3s), then red, and the cycle repeats with TL4 turning green.
4. The frequency of flashing of PL1/PL2 red light is generated using a 555 timer.
5. _This feature requires integration with subsystem three._ Upon detection of a vehicle by US5, if TL4 is currently not red, it should turn yellow (3s) then red. If TL5 is currently not red, it should turn yellow, then red. Then, PL1/PL2 turns green.When a vehicle is no longer detected by US5, the following sequence should execute:
    - PL1/PL2 should turn flashing red for 2s before resetting to solid red.
    - Then, TL4 should turn green.
    - TL4/TL5 should then resume the normal 2.R3 cycle.
   
## Subsystem 3
**Features:**
1. Upon detection of an overheight vehicle by US5, the following sequence should trigger to allow the vehicle to exit:
    1. TL6 turns green for 5s
    2. TL6 then turns yellow for 3s
    3. TL6 then turns back to red
2. If the ultrasonic sensor US5 continues to detect an overheight vehicle after TL6 has been green for 5s, TL6 continues to stay green until US5 no longer detects a vehicle.
3. If the ultrasonic sensor US5 continues to detect an overheight vehicle after TL6 has stayed green for 5s, the following sequence runs instead:
    1. TL6 flashes both green and yellow (at the same time) at 2-5 Hz continuously until US5 no longer detects an overheight vehicle
    2. TL6 turns back to red (otherwise (1) will continue).
4. The frequency of flashing green/yellow of TL6 at 2-5Hz is generated using a 555 timer.
5. _This feature requires integration with subsystem two._ Upon detection of an overheight vehicle by US5, 3.R1 sequence is delayed by 3s to allow for the Tunnel Ave traffic lights to turn red before allowing the exit traffic to move.

Subsystem 2&3:
![IMG_20251023_162139450](https://github.com/user-attachments/assets/262ed437-8a56-40be-a78d-4add5acc57b5)

## Subsystem 4
**Features:**
1. Upon detection of an overheight vehicle by US3, TL3 should turn from green to red immediately. The system can only reset to ‘normal state’ if an overheight vehicle is no longer detected by US3. (i.e. TL3 turns back to green)
2. The ultrasonic sensor US4 is used to verify data read by US3. US3 is only triggered if US4 reads the same value (within an acceptable error range).
3. Upon system start-up, the user is prompted to enter the overheight limit configuration for the system. If the user hits enter without providing any input, it defaults to the system default value of 4.0 meters. This value should be used as a variable in the entire subsystem.
4. _This feature requires integration with subsystem one, subsystem two and subsystem three._ Upon detection of an overheight vehicle by US3/US4, execute the following alternate behaviour:
     - The system reset to ‘normal state’ now relies on US5 detecting an overheight vehicle exiting and US1/US2/US3/US4/US5 no longer detecting an overheight vehicle
  
![IMG_20251023_162134774](https://github.com/user-attachments/assets/fead768f-60b8-4d64-a40b-1497cc05a429)

## Subsystem 5
_Note that subsystem 5 has no software component and is purely hardware based._
**Features:**
1. This subsystem is powered by an external battery supply and must not be powered by the Arduino’s pins. Upon detecting a loss of power to the Arduino (by monitoring the Arduino’s power pins), PA2 should start sounding an alert tone between 1000 Hz and 3000 Hz immediately. A 555 timer must be used to generate the tone. The alert tone should be clearly audible (not soft) but not excessive (not too loud).
2. The detection circuit (monitoring power loss from the Arduino) is done by implementing a comparator op-amp.
![IMG_20251023_162152669](https://github.com/user-attachments/assets/8f36caeb-e85b-4fc0-8c80-5c9c55c116df)
