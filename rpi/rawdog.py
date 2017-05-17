#!/usr/bin/env python3

import RPi.GPIO as gpio
import time

dclk = 3
ddat = 2
st = 0.02

curr_clock = True

def init(nst):
    global st
    st = nst
    gpio.setmode(gpio.BCM)
    gpio.setwarnings(True)
    gpio.setup(dclk, gpio.OUT)
    gpio.setup(ddat, gpio.OUT)
    gpio.output(dclk, 1)
    curr_clock = True


def sendHalfBit(bit):
    global curr_clock
    gpio.output(ddat, bit)
    time.sleep(st)
    curr_clock = not curr_clock
    gpio.output(dclk,curr_clock)
    time.sleep(st)

def sendWholeBit(bit):
    sendHalfBit(not bit)
    sendHalfBit(bit)

def sendReset():
    sendHalfBit(0)
    sendHalfBit(0)
    sendHalfBit(0)
    sendWholeBit(1)

def sendWord(w):
    sendReset()
    sendWholeBit(1)
    for j in range(32):
        bit = (w >> (31-j)) & 0x1
        sendWholeBit(bit)

def recvHalfBit():
    global curr_clock
    curr_clock = not curr_clock
    gpio.output(dclk,curr_clock)
    time.sleep(st)
    val = gpio.input(ddat)
    time.sleep(st)
    return val

def recvBit():
    v0 = recvHalfBit()
    v1 = recvHalfBit()
    return v1


def readWord():
    sendReset()
    sendWholeBit(0)
    gpio.setup(ddat, gpio.IN)
    w = 0
    for bitnum in range(32):
        b = recvBit()
        w >>= 1
        w |= (b << 31)
    gpio.setup(ddat, gpio.OUT)
    return w

def done():
    gpio.cleanup()


if __name__ == '__main__':
    init(0.040)

    sendHalfBit(0)
    sendHalfBit(0)
    sendHalfBit(0)

    sendWholeBit(1)

    sendWholeBit(1)

    sendWholeBit(1)
    sendWholeBit(1)
    sendWholeBit(1)
    sendWholeBit(1)
    sendWholeBit(0)
    sendWholeBit(0)
    sendWholeBit(0)
    sendWholeBit(0)
    sendWholeBit(1)
    sendWholeBit(1)
    sendWholeBit(1)
    sendWholeBit(1)
    sendWholeBit(0)
    sendWholeBit(0)
    sendWholeBit(0)
    sendWholeBit(0)

    gpio.cleanup()

