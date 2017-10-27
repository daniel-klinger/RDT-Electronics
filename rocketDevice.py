# code for the pi in the rocket

import SMBus
import math
import serial
import BerryImu
import GPIO
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
import RPi.GPIO as GPIO
import threading
from queue import Queue
from BerryImu import *
from collections import OrderedDict

# boolean to stop everything when done
stop = false;
# dictionary for messages to be stored
messages = OrderedDict()
# queue for data to be passed to the antenna with
dataQueue = queue.Queue()

#Initiliazation of I2C bus
bus = smbus.SMBus(1)

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

def magnitude(x, y, z):
    return math.sqrt(x*x+y*y+z*z)

def readWordTwosComp(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr + 1)
    val = (high << 8) + low
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val


def getBerryImuData():
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
    accelX = berryImu.readACCx()
    accelY = berryImu.readACCy()
    accelZ = berryImu.readACCz()

    magX = berryImu.readMAGx()
    magY = berryImu.readMAGy()
    magZ = berryImu.readMAGz()
    
    gyrX = berryImu.readGYRx()      
    gyrY = berryImu.readGYRy()        
    gyrZ = berryImu.readGYRz()

    tempAndPress = berryImu.getTempAndPressure()




                
def setup():
  # Setting power register to start getting sesnor data
  bus.write_byte_data(address, power_mgmt_1, 0)

  # Setting Acceleration register to set the sensitivity
  # 0,8,16 and 24 for 16384,8192,4096 and 2048 sensitivity respectively
  bus.write_byte_data(address, accel_config, 24)

  # Setting gyroscope register to set the sensitivity
  # 0,8,16 and 24 for 131,65.5,32.8 and 16.4 sensitivity respectively
  bus.write_byte_data(address, gyro_config, 24)


        
if __name__ == "__main__":
  setup()
  try:
    print("running")
  except KeyboardInterrupt:
    pass

    
