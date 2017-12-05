Overall Design Goal:
  Design telemetry sending and receiving suite to get the most data possible
  
For Nikomedes Launch:
  Ground code to receive incoming data and log it to screen and file with timestamps
  In-Rocket Code to receive data from various sensors and pass this data to the antenna to be sent
  Launch is at start of November. Should be completely finished and tested before Halloween
  
For full launch:
  Ground code with full-featured GUI, ideally parses incoming data and does data analysis. Would ideally have GPS map tracking, graphs of
    altitude, pressure, orientation. Also telemetry info showing packet loss rate, data link rate. Everything recorded, either to
    monolithic log file or separated and organized on some db or other relational structure
    May include being activated by a series of button presses and switches from GPIO
  May or may not have scrath-coded telemetry on the rocket itself. Will probably be data sent from altimeters.

  
Ground Code:
  1. Constantly reads serial data from antenna as it comes in
  2. Parses data received. 
  3. Writes both raw and parsed data to file
  4. Writes parsed data to stdout when it is different from previous data (you should be sending constantly to maximize chance of packets getting through)
  5. Bonus: Tell when connection is lost (have timeout on serial, display when timeout is passed as no connection)
  6. Bonus: Determine and display packet loss (if you are sending at a moderately constant rate, just do "actual packets per second / expected packets per second" or something
  
  Structure:
    Initialization of things
    Main Loop (exit on KeyboardInterrupt Error)
      Wait for serial messages (have a delimeter to determine the end of a "message")
      Write raw message to file (use logger, probably debug, and then screen has a minimum of info)
      Parse message
      Write parsed message to file
      If parsed message is different than last parsed message, display to screen

      
Rocket Code:
  This will be threaded. Each thread should represent a different interface. The interfaces are as follows
  1. USB Serial to Antenna
  2. I2C Ports to BerryIMU - Gives back accelerometer x,y,z, gyroscope x,y,z, and pressure (This may be on the tilt check, see 4.c
  3. GPS over GPIO Serial ports. This sends configurable data at 1HZ (can be configured up to 10Hz)
      Use my python library for interacting with this
  4. Waiting for several GPIO pins to have voltage across them (GPIO pin will be pulled high). 
      
      a) The lux sensor will pull high when there is light. As long as it is high we want to know that
      
      b) There will be 2 different altimeters will pull high for a certain fraction of a second (ask Dan what time range you should be concerned about)
          After they have pulled, we want to continuously send that they have pulled (so have a toggle)
      
      c) Also there will be a tilt check also hooked up to a GPIO. On the ground, we want it VERY obvious if this pulls high (it means the rocket is tilted sideways)
          We might actually connect this over SPI, in which case you will be sending BerryIMU data from this
          
  Structure:
  Initialize things. Define interfaces that can be used by multiple threads (message queues, synchronous lists, etc.)

  Define your thread functions
    Antenna should maintain a list of last message from each thread (or something), poll a message queue, then send data to radio over serial
    All other threads are basically polling their interface, sending a message to queue if necessary

  Run all threads

GUI Ideas:

Using matplotlib for the graphs. Probably implement a PyQt5 backend so that we can use tabs. Tabs are to best use the limited screen space, and we don't have to render
 each graph for every update, only the one we're looking at.
 
Graphs:
  Orientation of the rocket
  Map of GPS vs starting (plot path)
  GPIO Pins on/off
  Packet loss % as number (maybe line plot?)
  Temperature and pressure line graphs
  Acceleration line graph
  Signal strength

Updating graphs: Use an animate function, update 2 Hz (500ms)

Graphing setup should be on a separate thread from data collection

Make it pretty
