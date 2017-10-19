#!/usr/bin/python
#    Copyright (C) 2016  Mark Williams
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Library General Public
#    License as published by the Free Software Foundation; either
#    version 2 of the License, or (at your option) any later version.
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#    Library General Public License for more details.
#    You should have received a copy of the GNU Library General Public
#    License along with this library; if not, write to the Free
#    Software Foundation, Inc., 59 Temple Place - Suite 330, Boston,
#    MA 02111-1307, USA


import smbus
from LSM9DS0 import *
import time
from time import sleep
from ctypes import c_short

bus = smbus.SMBus(1)

addr = 0x77
oversampling = 3        # 0..3

class BerryImu():
  def __init__(self):
    #initialise the accelerometer
    self.writeACC(CTRL_REG1_XM, 0b01100111) #z,y,x axis enabled, continuos update,  100Hz data rate
    self.writeACC(CTRL_REG2_XM, 0b00100000) #+/- 16G full scale

    #initialise the magnetometer
    self.writeMAG(CTRL_REG5_XM, 0b11110000) #Temp enable, M data rate = 50Hz
    self.writeMAG(CTRL_REG6_XM, 0b01100000) #+/-12gauss
    self.writeMAG(CTRL_REG7_XM, 0b00000000) #Continuous-conversion mode

    #initialise the gyroscope
    self.writeGRY(CTRL_REG1_G, 0b00001111) #Normal power mode, all axes enabled
    self.writeGRY(CTRL_REG4_G, 0b00110000) #Continuos update, 2000 dps full scale


  def writeACC(self, register,value):
      bus.write_byte_data(ACC_ADDRESS , register, value)
      return -1

  def writeMAG(self, register,value):
      bus.write_byte_data(MAG_ADDRESS, register, value)
      return -1

  def writeGRY(self, register,value):
      bus.write_byte_data(GYR_ADDRESS, register, value)
      return -1



  def readACCx(self):
      acc_l = bus.read_byte_data(ACC_ADDRESS, OUT_X_L_A)
      acc_h = bus.read_byte_data(ACC_ADDRESS, OUT_X_H_A)
      acc_combined = (acc_l | acc_h <<8)
      return acc_combined  if acc_combined < 32768 else acc_combined - 65536


  def readACCy(self):
      acc_l = bus.read_byte_data(ACC_ADDRESS, OUT_Y_L_A)
      acc_h = bus.read_byte_data(ACC_ADDRESS, OUT_Y_H_A)
      acc_combined = (acc_l | acc_h <<8)
      return acc_combined  if acc_combined < 32768 else acc_combined - 65536


  def readACCz(self):
      acc_l = bus.read_byte_data(ACC_ADDRESS, OUT_Z_L_A)
      acc_h = bus.read_byte_data(ACC_ADDRESS, OUT_Z_H_A)
      acc_combined = (acc_l | acc_h <<8)
      return acc_combined  if acc_combined < 32768 else acc_combined - 65536


  def readMAGx(self):
      mag_l = bus.read_byte_data(MAG_ADDRESS, OUT_X_L_M)
      mag_h = bus.read_byte_data(MAG_ADDRESS, OUT_X_H_M)
      mag_combined = (mag_l | mag_h <<8)

      return mag_combined  if mag_combined < 32768 else mag_combined - 65536


  def readMAGy(self):
      mag_l = bus.read_byte_data(MAG_ADDRESS, OUT_Y_L_M)
      mag_h = bus.read_byte_data(MAG_ADDRESS, OUT_Y_H_M)
      mag_combined = (mag_l | mag_h <<8)

      return mag_combined  if mag_combined < 32768 else mag_combined - 65536


  def readMAGz(self):
      mag_l = bus.read_byte_data(MAG_ADDRESS, OUT_Z_L_M)
      mag_h = bus.read_byte_data(MAG_ADDRESS, OUT_Z_H_M)
      mag_combined = (mag_l | mag_h <<8)

      return mag_combined  if mag_combined < 32768 else mag_combined - 65536



  def readGYRx(self):
      gyr_l = bus.read_byte_data(GYR_ADDRESS, OUT_X_L_G)
      gyr_h = bus.read_byte_data(GYR_ADDRESS, OUT_X_H_G)
      gyr_combined = (gyr_l | gyr_h <<8)

      return gyr_combined  if gyr_combined < 32768 else gyr_combined - 65536
    

  def readGYRy(self):
      gyr_l = bus.read_byte_data(GYR_ADDRESS, OUT_Y_L_G)
      gyr_h = bus.read_byte_data(GYR_ADDRESS, OUT_Y_H_G)
      gyr_combined = (gyr_l | gyr_h <<8)

      return gyr_combined  if gyr_combined < 32768 else gyr_combined - 65536

  def readGYRz(self):
      gyr_l = bus.read_byte_data(GYR_ADDRESS, OUT_Z_L_G)
      gyr_h = bus.read_byte_data(GYR_ADDRESS, OUT_Z_H_G)
      gyr_combined = (gyr_l | gyr_h <<8)

      return gyr_combined  if gyr_combined < 32768 else gyr_combined - 65536
   
  def get_short(self, data, index):
    return c_short((data[index] << 8) + data[index + 1]).value

  def get_ushort(self, data, index):
    return (data[index] << 8) + data[index + 1]

  def getTempAndPressure(self):
    toReturn="";
    #(chip_id, version) = bus.read_i2c_block_data(addr, 0xD0, 2)
    #toReturn=toReturn+"Chip Id:"+ str(chip_id)+ "Version:"+ str(version)
    # Read whole calibration EEPROM data
    cal = bus.read_i2c_block_data(addr, 0xAA, 22)
    # Convert byte data to word values
    ac1 = self.get_short(cal, 0)
    ac2 = self.get_short(cal, 2)
    ac3 = self.get_short(cal, 4)
    ac4 = self.get_ushort(cal, 6)
    ac5 = self.get_ushort(cal, 8)
    ac6 = self.get_ushort(cal, 10)
    b1 = self.get_short(cal, 12)
    b2 = self.get_short(cal, 14)
    mb = self.get_short(cal, 16)
    mc = self.get_short(cal, 18)
    md = self.get_short(cal, 20)
    bus.write_byte_data(addr, 0xF4, 0x2E)
    sleep(0.005)
    (msb, lsb) = bus.read_i2c_block_data(addr, 0xF6, 2)
    ut = (msb << 8) + lsb
    bus.write_byte_data(addr, 0xF4, 0x34 + (oversampling << 6))
    sleep(0.04)
    (msb, lsb, xsb) = bus.read_i2c_block_data(addr, 0xF6, 3)
    up = ((msb << 16) + (lsb << 8) + xsb) >> (8 - oversampling)
    x1 = ((ut - ac6) * ac5) >> 15
    x2 = (mc << 11) / (x1 + md)
    b5 = x1 + x2 
    t = int(b5 + 8) >> 4
    b6 = b5 - 4000
    b62 = int(b6 * b6) >> 12
    x1 = (b2 * b62) >> 11
    x2 = int(ac2 * b6) >> 11
    x3 = x1 + x2
    b3 = (((ac1 * 4 + x3) << oversampling) + 2) >> 2
    x1 = int(ac3 * b6) >> 13
    x2 = (b1 * b62) >> 16
    x3 = ((x1 + x2) + 2) >> 2
    b4 = (ac4 * (x3 + 32768)) >> 15
    b7 = (up - b3) * (50000 >> oversampling)
    p = (b7 * 2) / b4
    #p = (b7 / b4) * 2
    x1 = (int(p) >> 8) * (int(p) >> 8)
    x1 = (x1 * 3038) >> 16
    x2 = int(-7357 * p) >> 16
    p = p + ((x1 + x2 + 3791) >> 4)
    toReturn=toReturn+"Temperature:"+str(t/10.0)+ "C"
    toReturn=toReturn+"Pressure:"+ str(p / 100.0)+ "hPa"
    return toReturn