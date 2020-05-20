#!/usr/bin/env python3

import time
from smbus import SMBus
import RPi.GPIO as GPIO

class rigmi2c(object):
    def __init__(self):
        self.bus = SMBus(1)
        self.addr = 42

    def readall(self):
        try:
            data = self.bus.read_i2c_block_data(self.addr, 1, 32)
            time.sleep(0.050) # necessary to avoid some kind of i2c error
            rd = []
            for i in range(16):
                rd.append(data[2*i] | (data[1+2*i] << 8))
            return rd 
        except Exception as e:
            print("Exception while reading.")
            print(e)
            self.reset_Ard()
            return None

    def _writeReg(self,cmd,addr,val):
        addr &= 0xf
        cmd &= 0xf
        c  = (cmd << 4) | addr
        d1 = (val >> 8) & 0xff
        d0 = val & 0xff
        try:
            self.bus.write_i2c_block_data(self.addr,c,[d1,d0])
        except Exception as e:
            self.reset_Ard()

        time.sleep(0.050) # necessary to avoid some kind of i2c error


    def reset_Ard(self):
        print('Resetting Atmega')
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(7,GPIO.OUT)
        GPIO.output(7,GPIO.LOW)
        GPIO.output(7,GPIO.HIGH)
        time.sleep(0.020) 
        GPIO.output(7,GPIO.LOW)
        GPIO.setup(7,GPIO.IN)


    def setWord(self,addr,bits):
        self._writeReg(0,addr,bits)

    def setBits(self,addr,bits):
        self._writeReg(1,addr,bits)

    def clrBits(self,addr,bits):
        self._writeReg(2,addr,bits)

    def tglBits(self,addr,bits):
        self._writeReg(3,addr,bits)



if __name__ == '__main__':
    r = rigmi2c()

    if True:
        for i in range(16):
            r.setWord(i,0x1111 * i)
       
    if True:
        r.setWord(6,0xffff)

    if True:
        print('readall', r.readall())
