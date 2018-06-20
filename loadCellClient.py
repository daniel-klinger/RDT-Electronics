#Connects to the master via wifi, connects to the load cell via SPI.

from queue import Queue
import logging, socket, sys, threading, time

try:
  import RPi.GPIO as gpio
except ImportError:
  #Make a dummy gpio for testing
  class _meta(type):
    def __getattr__(cls, name):
      return _meta._defaultFunction
    @staticmethod
    def _defaultFunction(*arg, **kwarg):
      pass
  class gpio(metaclass=_meta):
    def input(*arg, **kwarg):
      return True

#Inpsiration taken from https://github.com/tatobari/hx711py/blob/master/hx711.py
      
#Synchronization Tools
readingQueue = Queue()
stopSignal = threading.Event()

#Pin settings
PIN_MODE = gpio.BCM
PIN_CLOCK = 18
PIN_DATA  = 4

GAIN = 64

#If this is none, will check a small range for connections
SERVER_IP = None
PORT = 9999 #Arbitrary

logging.basicConfig(format="%(asctime)s [%(threadName)s] [%(levelname)s]  %(message)s", level=logging.DEBUG, handlers = [
  logging.StreamHandler(),
  logging.FileHandler("loadCell.log", mode="w"),
])
logger = logging

def init():
  logger.debug("Setting up pins")
  #Then setup pins
  gpio.setmode(PIN_MODE)
  gpio.setup(PIN_CLOCK, gpio.OUT)
  gpio.setup(PIN_DATA, gpio.IN)
  #Ensure it is pulled low
  gpio.output(PIN_CLOCK, False)
  time.sleep(0.0001) #Ensure it has time to turn on
  

def processReadings(ipInfo):
  logging.debug("Starting Processor Thread")
  buffer = []
  bufferSize = 10 #We read at ~10 Hz, so just send like once a second
  while not stopSignal.is_set():
    reading = readingQueue.get() #Will block until it has a reading
    
    #Format as time, value, gain, output value (strain)
    string = "T:{}, V:{}, G:{}, O:{}".format(*reading)
    logger.info(string)
    
    #Handle sending data to remote host for transmission
    if ipInfo is not None:
      buffer.append(reading[-1]) #Just get the output value
      if len(buffer) >= bufferSize:
        #opens a connection, then closes it once the data has been sent
        dataToSend = sum(buffer)/len(buffer) #Get an average
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
          s.connect(ipInfo)
          #Send average of strains
          s.sendall(bytes(str(dataToSend), encoding="utf-8"))
        buffer.clear() #Then clear it

#Processes a raw reading, and gives out string
def createReading(value):
  output = value #This is temporary. Ideally we should be transmitting strain, but I don't know the equation.
  #Send a 4-tuple of necessary info
  readingQueue.put((time.time(), value, GAIN, output))
  
def getValue(tare, timeout=None):
  start = time.time()
  #Wait for output pin to go low, then pulse proper number of times
  while gpio.input(PIN_DATA): #Just busy wait here
      if timeout is not None and time.time() - start > timeout:
        raise RuntimeError("timeout")
  
  rawValue = 0
  for i in range(24):
    #Pulse the pin. These should last the requisite time
    gpio.output(PIN_CLOCK, True)
    gpio.output(PIN_CLOCK, False)
    #On falling signal, next bit should be set, we can read it
    #  add 1 in the proper position if pin high, otherwise 0
    rawValue += int(gpio.input(PIN_DATA)) * 1 << (24-i-1)
    
  #Pulse the pin this many times
  for i in range(1 if GAIN == 128 else (2 if GAIN == 32 else 3)):
    gpio.output(PIN_CLOCK, True)
    gpio.output(PIN_CLOCK, False)
  
  #"The 25th pulse at PD_SCK input will pull DOUT pin back to high"
  #  If it has not, we have a communication error and need to reset
  if not gpio.input(PIN_DATA):
    logging.error("data pin not high after reading data! Resetting board")
    #Setting pin to high for > 60 us will turn board off, setting low turns board back on.
    gpio.output(PIN_CLOCK, False)
    gpio.output(PIN_CLOCK, True)
    time.sleep(0.0001)
    GPIO.output(PIN_CLOCK, False)
    time.sleep(0.0001)
    
  #Then process the value
  #  We have a 3-byte signed integer that we are storing in an unsigned integer. This will convert it to a proper signed integer
  #  The value represents a percentage of the maximum range
  #  The range of a 3-byte signed int is -2**23 : 2**23 - 1, so we'll just take the division of 2**23, as it should normally be positive anyway
  #  The HX711 has a maximum read range of +-0.5/GAIN volts, so multiply it by that
  #  Finally, subtract the tared value
  return int.from_bytes(rawValue.to_bytes(3, byteorder="big", signed=False), byteorder="big", signed=True) / 2**(24-1) * (0.5/GAIN) - tare
    
def getLoadCellReadings(tare):
  logging.debug("Starting Load Cell Thread")
  while not stopSignal.is_set():
    #Do a reading
    value = getValue(tare)
    
    #Then put it in queue to be sent, along with adjusting to strain
    readingQueue.put(createReading(value))

def main():
  logger.debug("Starting Process!")
  
  #First check wifi
  for ip in (SERVER_IP,) if SERVER_IP is not None else ["192.168.0.{}".format(i) for i in range(1,9)]:
    logger.debug("Checking IP address for connection: "+ip)
    try:
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0) #1 second for each
        s.connect((ip, PORT))
      logger.debug("Success!")
      ipInfo = (ip, PORT) #Set this for transmission
      break
    except (socket.timeout, OSError):
     logger.debug("Failure!")
  else: #If no ips worked
    logger.debug("No ip address was a valid server. Disabling wifi transmission")
    ipInfo = None
  
  #Setup pins
  init()
  
  #Get a tare reading
  try:
    tare = getValue(0, timeout=5)
  except RuntimeError:
    logging.error("Tare timeout exceeded, this does not bode well")
    tare = 0
  logging.info("Tare Reading: "+str(tare))
  
  #Set up threads
  loadCellThread = threading.Thread(target=getLoadCellReadings, name="LoadCell ", args=(tare,))
  processorThread = threading.Thread(target=processReadings, name="Processor", args=(ipInfo,))
  
  try:
    #Start both threads
    loadCellThread.start()
    processorThread.start()
    
    #Wait for both threads to finish
    loadCellThread.join()
    processorThread.join()
  finally: #Will happen on error, also normal
    logger.debug("Exiting")
    stopSignal.set() #On exit, tell both threads to stop
  
if __name__ == "__main__":
  main()