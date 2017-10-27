'''
serial - for sending data to and from external devices like the accelerometer
sys - for information about hardware on this system
math - for math related functions
logging - for clear and pretty output 
'''
import serial
import sys
import logging

# create formatters for the logger
format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s)')
rawformat = logging.Formatter('%(message)s)')
# initialize our logger
logger = logging.getLogger("groundServer")
logger.setLevel(logging.DEBUG)
# create a file to log data to
fileHandler = logging.FileHandler("data.log", mode = "a", delay = True)
fileHandler.setFormatter(format)
logger.addHandler(fileHandler)
# create file to log raw data to
fileHandler = logging.FileHandler("raw.log", mode = "a", delay = True)
fileHandler.setFormatter(rawformat)
logger.addHandler(fileHandler)
# create a handler that prints out thing to stdout
outHandler = logging.StreamHandler(sys.stdout)
outHandler.setFormatter(format)
logger.addHandler(outHandler)
# set the level to info so we don't get so much spam
logger.setLeve(logging.INFO)
    
if __name__ == "__main__":
  try:
    logger.info("Initializing serial connection and antenna...")
    ser = serial.Serial('/dev/ttyUSB0', 9600)
    ser.open()
    while True:
      # read one byte at a time until we read newline character
      # then log the message that was received.
      stringBuffer = ''
      charFromStream = ''
      while charFromStream != '\n':
        charFromStream = ser.read(1).decode("utf-8")
        if charFromStream != '\n':
          stringBuffer += charFromStream
      logger.debug("Message: %s", stringBuffer)      
  except KeyboardInterrupt:
    pass