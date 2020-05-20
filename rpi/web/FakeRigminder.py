#!/usr/bin/env python3

import json
import datetime
import random
import math
import time
import asyncio

class Device:
    def __init__(self):
        print('FakeDevice __init__')
        self.inited = True
        self.q = asyncio.PriorityQueue()

        self.reg_numbers = {
           'REG_VIN': 0,
           'REG_VOUT': 1,
           'REG_OUTPUT': 6,
           'REG_WDOG_MASK': 5,
           'REG_TIMER': 7,
        }

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
                    if reg_name in ['REG_VIN', 'REG_VOUT']:
                        self.device_status['registers'][reg_name] = {
                            'value': random.randint(0,1023),
                            'last_update': datetime.datetime.now(),
                        }
                    elif reg_name == 'REG_TIMER':
                        tv = self.device_status['registers']['REG_TIMER'].get('value',0);
                        tv -= 1
                        if tv <= 0:
                            tv = 0 
                            ov = self.device_status['registers']['REG_OUTPUT'].get('value',0)
                            mv = self.device_status['registers']['REG_WDOG_MASK'].get('value',0)
                           
                            ov &= ~mv
                            self.device_status['registers']['REG_WDOG_MASK'] = {
                                'value': ov,
                                'last_update': datetime.datetime.now(),
                            }

                        self.device_status['registers']['REG_TIMER'] = {
                            'value': tv,
                            'last_update': datetime.datetime.now(),
                        }
 

                elif qi[1] == 'write':
                    reg_name = qi[2]
                    reg_val = qi[3]
                    self.device_status['registers'][reg_name] = {
                        'value': reg_val,
                        'last_update': datetime.datetime.now(),
                        }

                yield from asyncio.sleep(0.5)

 

    def readStatus(self):
        return self.device_status


