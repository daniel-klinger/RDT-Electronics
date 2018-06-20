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

# create formatters for the logger
format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s)')
# initialize our logger
logger = logging.getLogger("rocketDevice")
logger.setLevel(logging.DEBUG)
# create a file to log data to
fileHandler = logging.FileHandler("flight.log", mode = "a", delay = False)
fileHandler.setFormatter(format)
logger.addHandler(fileHandler)


class DataHandler():
  lastData = OrderedDict = {} #Dict of threadName: data. The last piece of data sent by this thread
  dataLock = threading.Lock()
  
  def __init__(self, name, *args):
    self.name = name
    self.lastData[name] = ""
    self.initialize(*args)
    
  @classmethod
  def getThread(cls, name, initArgs=[], threadArgs=[]):
    newObj = cls(name, *initArgs) #Initialize
    return threading.Thread(target = newObj.runThread, name=name, args=*threadArgs)
    
  def runThread(self, *args):
    while True:
      try:
        newData = self.getData(*args)
        logger.info(self.format(newData)) #Just log the new data. Thread and timestamp should be included
        with self.dataLock: #Make sure that we aren't modifying data as it's sent
          self.lastData[self.name] = newData
      except Exception as e:
        logger.exception("Thread has encountered an exception on data aquisition")
        
  def initialize(self, *args):
    raise NotImplementedError("initialize should be subclassed")
  
  def getData(self, *args):
    raise NotImplementedError("getData should be subclassed")

  #Format a log entry. Intended to be subclassed if necessary
  def format(self, data):
    return str(data)

class BerryImuHandler(DataHandler):
  """
  Includes Gyroscope, Magnetometer, Temperature, Pressure, and GPS
  """

  def initialize(self, *args):
    self.berryImu = BerryImu()
    self.dataFormat = createDataString(11)
    
  def getData(self, *args):
    pass
    #INSERT REAL BERRY IMU HANDLING HERE
    # get readings for acceleration
    accelX = self.berryImu.readACCx()
    accelY = self.berryImu.readACCy()
    accelZ = self.berryImu.readACCz()
    # get readings for magnetometer
    magX = self.berryImu.readMAGx()
    magY = self.berryImu.readMAGy()
    magZ = self.berryImu.readMAGz()
    # get readings from the gyroscope
    gyrX = self.berryImu.readGYRx()
    gyrY = self.berryImu.readGYRy()
    gyrZ = self.berryImu.readGYRz()
    # get temperature and pressure readings
    temp, press = self.berryImu.getTemperatureAndPressure()
    # add all data to the queue as a string
    addToQueue(dataFormat.format(accelX, accelY, accelZ,
                                 magX, magY, magZ,
                                 gyrX, gyrY, gyrZ,
                                 temp, press))
    

class LoadCellHandler():
  def initialize(self, *args):
    self.socket = s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 9999)) #Bind on local host, port 9999
    s.listen(5) #Accept up to 5 connections at once
    
  def getData(self, *args):
    conn, address = self.socket.accept() #Wait for a connection
    data = conn.recv(4096).decode("utf-8") #Get the data, decoding it
    conn.close() #Close the connection
    return str(round(data, 2)) #Forward the data, rounded to 2 decimals
    
# this functions pulls data (message) off of the queue and sends it
# as a broadcast for the other antenna to receive
def antenna(ser):
  timeInterval = 0.5 #In seconds
  while True:
    with DataHandler.dataLock:
      buffer = "|".join(DataHandler.lastData.values()) #Add together all the values, comma separated
      log.info("Sending Values: '{}'".format(buffer))
      ser.write(bytes(buffer), "utf-8")

"""
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
"""
    
# creates a string like '{:.2f}, {:.2f}...' to be filled with data
# if you want non truncated data, set truncated to false
def createDataString(numElements, truncated = True):
  if (truncated):
    return ", ".join(["{:.2f}" for i in range(numElements)])
  else:
    return ", ".join(["{}" for i in range(numElements)])


if __name__ == "__main__":
  logger.info("Initializing serial connection and antenna...")
  ser = serial.Serial('/dev/ttyUSB0', 9600)
  ser.open()
  
  # set up the threads for collecting data from each sensor and the antenna
  antennaThread = threading.Thread(target = antenna, name = "antenna", args = (ser,))
  berryImuThread = BerryImuHandler.getThread("berryImu")
  payloadThread  = LoadCellHandler.getThread("loadCell")
  threads = [antennaThread, berryImuThread, payloadThread]
  try:
    # start all threads
    for t in threads:
      t.start()
    # sit here until all threads are done threading
    for t in threads:
      t.join()
  except KeyboardInterrupt:
    pass

    
