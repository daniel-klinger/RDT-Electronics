'''
serial - for sending data to and from external devices like the accelerometer
sys - for information about hardware on this system
math - for math related functions
logging - for clear and pretty output 
'''
import serial
import sys
import logging

# initialize our logger
logger = logging.getLogger("groundServer")
logger.setLevel(logging.DEBUG)
format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
fileHandler = logging.FileHandler("data.log", mode = "a", delay = True)
fileHandler.setFormatter(format)
logger.addHandler(fileHandler)
outHandler = logging.StreamHandler(sys.stdout)
outHandler.setFormatter(format)
logger.addHandler(outHandler)
    
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
            logger.info("Message: %s", stringBuffer)      
    except KeyboardInterrupt:
        pass