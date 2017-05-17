#!/usr/bin/env python3

import json
import datetime
import random
import math
import time
import dogcmds as wdog
import asyncio

class Device:
    def __init__(self):
        print('RealDevice __init__')
        wdog.init(0.00250)
        self.inited = True
        self.q = asyncio.PriorityQueue()

        self.reg_numbers = {
           'REG_VIN': 0,
           'REG_VOUT': 1,
           'REG_OUTPUT': 6,
           'REG_WDOG_MASK': 5,
           'REG_TIMER': 7,
        }

        wdog.setWord(self.reg_numbers['REG_TIMER'],60)
        wdog.setWord(self.reg_numbers['REG_OUTPUT'],0xffff)

        self.bitmasks = {
            'OUT_MASK_DC': 0x1,
            'OUT_MASK_AC': 0x8,
            'OUT_MASK_LED': 0x2,
            'OUT_MASK_OC': 0x4,
        }

        self.device_status = {
            'count': 0,
            'registers': {
                'REG_VIN': {},
                'REG_VOUT': {},
                'REG_OUTPUT': {},
                'REG_WDOG_MASK': {},
                'REG_TIMER': {},
            }
        }


    def resetTimer(self,tval):
        self.q.put_nowait((0,'write','REG_TIMER',tval))
        self.q.put_nowait((0,'read','REG_TIMER'))
        return { 'result': 'OK' }

    def setOutput(self,oval):
        self.q.put_nowait((1,'write','REG_OUTPUT',oval))
        self.q.put_nowait((1,'read','REG_OUTPUT'))
        return { 'result': 'OK' }

    def setResetMask(self,msk):
        self.q.put_nowait((2,'write','REG_WDOG_MASK',msk))
        self.q.put_nowait((2,'read','REG_OUTPUT'))
        return { 'result': 'OK' }

    def printHex(self,v):
        print("val: 0x{:04x}, cmd: 0x{:04x}".format(v['val'],v['cmd']))

    @asyncio.coroutine
    def queueFiller(self):
        keep_running = True
        while keep_running:
            if self.q.empty():
                print('qF() refilling')
                for reg_name in self.reg_numbers:
                    x = (10,'read',reg_name)
                    self.q.put_nowait(x)
            yield from asyncio.sleep(1)

    @asyncio.coroutine
    def queueHandler(self):
        keep_running = True
        print('handleCommands()') 
        while keep_running:
            while True:
                qi = yield from self.q.get()
                print(qi)
                if qi[1] == 'read':
                    reg_name = qi[2]
                    rv = wdog.getWord(self.reg_numbers[reg_name])
                    self.printHex(rv)
                    if rv['cmd'] == 0:
                        self.device_status['registers'][reg_name] = {
                            'value': rv['val'],
                            'last_update': datetime.datetime.now(),
                        }
                elif qi[1] == 'write':
                    reg_name = qi[2]
                    reg_val = qi[3]
                    wdog.setWord(self.reg_numbers[reg_name],reg_val)

                yield from asyncio.sleep(0.5)

 

    def readStatus(self):
        return self.device_status


