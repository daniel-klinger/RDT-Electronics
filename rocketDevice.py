# code for the pi in the rocket

import SMBus
import math
import serial
import BerryImu
import GPIO
from queue import queue

stop = false;
dataQueue = queue.Queue()

#Initiliazation of I2C bus
bus = smbus.SMBus(1)
address = 0x68       # Sensor I2C address
address_mag = 0x0c   #Sensor address for magnetometer

# Register address from MPU 9255 register map
power_mgmt_1 = 0x6b
usr_cntrl = 0x6a
int_pin_conf = 0x37
cntrl = 0x0a
mag_xout_h = 0x03
mag_yout_h = 0x05
mag_zout_h = 0x07
gyro_config = 0x1b
gyro_xout_h = 0x43
gyro_yout_h = 0x45
gyro_zout_h = 0x47
accel_config = 0x1c
accel_xout_h = 0x3b
accel_yout_h = 0x3d
accel_zout_h = 0x3f

# this functions pulls data (message) off of the queue and sends it
# as a broadcast for the other antenna to receive
def antenna(ser):
    while True:
        try:
            data = dataQueue.get(block = True, timeout = 5)
            ser.write(bytes(data, "utf-8"))
        except Empty:
            pass
        finally:
            if stop:
                break

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

def AccelGyroPres():
    oldXAccel=0
    oldYAccel=0
    oldzAccel=0
    oldGyroX=0
    oldGyroY=0
    oldGyroZ=0
    rocketHasLaunched=False
    timeRocketLaunched=0
    
    while True:
        accelOutX = readWordTwosComp(accel_xout_h)
        accelOutY = readWordTwosComp(accel_yout_h)
        accelOutZ = readWordTwosComp(accel_zout_h)

        accelOutScaledX = accelOutX / 2048.0
        accelOutScaledY = accelOutY / 2048.0
        accelOutScaledZ = accelOutZ / 2048.0

        if ((accelOutScaledX > 1.5 or accelOutScaledY > 1.5 or accelOutScaledZ > 1.5)
            and (accelOutScaledX != oldXAccel or accelOutScaledY != oldYAccel or accelOutScaledZ != oldzAccel):
            mag = magnitude(accelOutScaledX,accelOutScaledY,accelOutScaledZ)
            if (mag > 5 and not rocketHasLaunched):
                rocketHasLaunched = true
                timeRocketLaunched = time.time()
                time.clock()
            if(mag <= 5 nd rocketHasLaunched):
                # figure out how data will be sent
            
            gyroOutX = readWordTwosComp(gyro_xout_h)
            gyroOutY = readWordTwosComp(gyro_yout_h)
            gyroOutZ = readWordTwosComp(gyro_zout_h)

            gyroOutScaledX = gyroOutX / 16.4
            gyroOutScaledY = gyroOutY / 16.4
            gyroOutScaledZ = gyroOutZ / 16.4

            if ((gyroOutScaledX-oldGyroX > 16 or gyroOutScaledY - oldGyroY > 16 or gyroOutScaledZ - oldGyroZ > 16)):
                # figure out how data will be sent
                oldGyroX = gyroOutScaledX
                oldGyroY = gyroOutScaledY
                oldGyroZ = gyroOutScaledZ


                
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

    