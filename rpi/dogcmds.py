#!/usr/bin/env python3

import rawdog as wdog;
import time

debug = False
def init(nst,ndebug = False):
    debug = ndebug
    wdog.init(nst)

def done():
    wdog.done()

def read():
    a = wdog.readWord()
    top = (a >> 16) & 0xffff
    bottom = a & 0xffff
    return { 'cmd': top, 'val': bottom }

def makeAndSendThing(x,addr,bits):
    cmd = ((x & 0xf) << 4) | (addr & 0xf) 
    word = (cmd << 16) | (bits & 0xffff)
    if debug:
        print("Sending word: {:08x}".format(word))
    wdog.sendWord(word)
    
def setWord(addr,bits):
    makeAndSendThing(0,addr,bits)

def setBits(addr,bits):
    makeAndSendThing(1,addr,bits)

def clearBits(addr,bits):
    makeAndSendThing(2,addr,bits)

def toggleBits(addr,bits):
    makeAndSendThing(3,addr,bits)

def getWord(addr):
    makeAndSendThing(4,addr,0)
    time.sleep(0.100)
    return read()

if __name__ == "__main__":
    init(0.040)
    wdog.sendWord(0xdeadbeef)
    #wdog.sendWord(0xa5a5)


