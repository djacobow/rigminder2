#!/usr/bin/env python3

import time
from smbus import SMBus

class rigmi2c(object):
    def __init__(self):
        self.bus = SMBus(1)
        self.addr = 42

    def readall(self):
        try:
            data = self.bus.read_i2c_block_data(self.addr, 1, 32)
            rd = []
            for i in range(16):
                rd.append(data[2*i] | (data[1+2*i] << 8))
            return rd 
        except Exception as e:
            print(e)
            return None

    def _writeReg(self,cmd,addr,val):
        addr &= 0xf
        cmd &= 0xf
        c  = (cmd << 4) | addr
        d1 = (val >> 8) & 0xff
        d0 = val & 0xff
        self.bus.write_i2c_block_data(self.addr,c,[d1,d0])
        time.sleep(0.020) # necessary to avoid some kind of i2c error

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
        r.setWord(0,0x1111)
        r.setWord(1,0x2222)
        r.setWord(2,0x3333)
        r.setWord(3,0x4444)
        r.setWord(4,0x5555)
        r.setWord(5,0x6666)
        r.setWord(6,0x7777)
        r.setWord(7,0x8888)
       
    if True:
        r.readall()
