# code for the pi in the rocket

import SMBus
import math
import serial
import BerryImu
import RPi.GPIO
import queue
import threading
from collections import OrderedDict
from GPSLib import GPS
from time import sleep

dataQueue = queue.Queue()

messages = OrderedDict()

# create formatters for the logger
format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s)')
# initialize our logger
logger = logging.getLogger("rocketDevice")
logger.setLevel(logging.DEBUG)
# create a file to log data to
fileHandler = logging.FileHandler("flight.log", mode = "a", delay = True)
fileHandler.setFormatter(format)
logger.addHandler(fileHandler)

def addToQueue(message):
  dataQueue.put([threading.current_thread(), message])

# this functions pulls data (message) off of the queue and sends it
# as a broadcast for the other antenna to receive
def antenna(ser):
    global messages
    while True:
        try:
            data = dataQueue.get(timeout = 0.05)
            #data = (threadName, message)
            messages[data[0]] = data[1]
            log.debug("Updated: '%s' to '%s'", data[0], data[1])
        except Empty:
            pass
        finally:
          ser.write(bytes("|".join(messages.values()), "utf-8"))

def berryImuData():
  berryImu = BerryImu()
  # string to be formatted with actual data
  data = createDataString(11)
  while True:
    # get readings for accelation
    accelX = berryImu.readACCx()
    accelY = berryImu.readACCy()
    accelZ = berryImu.readACCz()
    # get readings for magnetometer
    magX = berryImu.readMAGx()
    magY = berryImu.readMAGy()
    magZ = berryImu.readMAGz()
    # get readings from the gyroscope
    gyrX = berryImu.readGYRx()      
    gyrY = berryImu.readGYRy()        
    gyrZ = berryImu.readGYRz()
    # get temperature and pressure readings
    temp, press = berryImu.getTemperatureAndPressure()
    # add all data to the queue as a string
    addToQueue(data.format(accelX, accelY, accelZ,
                           magX, magY, magZ,
                           gyrX, gyrY, gyrZ,
                           temp, press))

def gpsData():
  gps = GPS()
  # create a string to be formatted by 
  data = createDataString(2, truncated = False)
  while True:
    lat, lng = GPS.getLocation()
    addToQueue(data.format(lat, lng))


def gpioData():
  import RPi.GPIO as G
  #Time between checking of pins
  #Ensure not shorter than antenna timeout, or will lose some data
  GPIO_WAIT_TIME = 0.1 #100ms
  #Dict that has the same order every time
  GPIOs = OrderedDict({[29]: "photo", [28]: "tilt"})
  
  #Initialize the pins
  G.setmode(G.BCM)
  #G.setup(0, G.UP) #Set pull-up resistor
  for pin in GPIOs: 
    G.setup(pin, G.IN)
  
  states = {pin: G.input(pin) for pin in GPIOs} #Get initial states of the pins
  #Dict of counters. Counter is set to 0 when a new state is detected.
  #Incremented by 1 each loop.
  counters = {pin: 0 for pin in GPIOs} 
  
  #Set up callbacks
  for pin in GPIOs:
    #This will this pin's changes to a list of pins to change
    G.add_event_detect(pin, G.BOTH)
    
  #Loop to wait for inputs to change
  while True:
    buffer = ""
    for pin in GPIOs:
      counters[pin] += 1
      if G.event_detected(pin):
        states[pin] = G.input(pin) #Update stored value
        counters[pin] = 0 
    
    #Every time we update timers, so every time we send message
    #Put the time in current state as hex, not exceeding 4 characters. Then put high or low on pin
    addToQueue("".join("{:04X}{:1d}".format(min(0xFFFF, counters[pin]), states[pin]) for pin in GPIOs))
    sleep(GPIO_WAIT_TIME) #Sleep between checking

# creates a string like '{:.2f}, {:.2f}...' to be filled with data
# if you want non truncated data, set truncated to false
def createDataString(numElements, truncated = True):
  
  if (truncated):
    return ", ".join(["{:.2f}" for i in range(numElements)])
  else:
    return ", ".join(["{}" for i in range(numElements)])


if __name__ == "__main__":
  # Ordered dict orders keys by when they were added
  # we always want them in this order so we can parse the data
  # on the ground with the correct values
  for i in ["berryImu", "gps", "gpio"]:
    messages[i] = None

  try:
    # set up the threads for collecting data from each sensor and the antenna
    antennaThread = threading.Thread(target = antenna, name = "antenna", args = (ser,))
    berryImuThread = threading.Thread(target = berryImuData, name = "berryImu")
    gpsThread = threading.Thread(target = gpsData, name = "gps")
    gpioThread = threading.Thread(target = gpioData, name = "gpio")
    threads = [antennaThread, berryImuThread, gpsThread, gpioThread]
    # start all threads
    for t in threads:
      t.start()
    # sit here until all threads are done threading
    for t in threads:
      t.join()
  except KeyboardInterrupt:
    pass

    
