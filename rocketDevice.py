# code for the pi in the rocket

import SMBus
import math
import serial
import BerryImu
import RPi.GPIO
import queue
import threading
from collections import OrderedDict

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
  oldXAccel = 0
  oldYAccel = 0
  oldzAccel = 0
  oldXMag = 0
  oldYMag = 0
  oldZMag = 0
  oldGyroX = 0
  oldGyroY = 0
  oldGyroZ = 0
  rocketHasLaunched = False
  timeRocketLaunched = 0
  berryImu = BerryImu()

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
    tempAndPress = berryImu.getTempAndPressure()

def gpsData():
  pass

def gpioData():
  pass   
   
if __name__ == "__main__":
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

    
