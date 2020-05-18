#!/usr/bin/env python3

import json
import datetime
import random
import math
import time
import rigmi2c
import asyncio

class Device:
    def __init__(self):
        print('RealDevice __init__')
        self.r = rigmi2c.rigmi2c()
        self.inited = True
        self.q = asyncio.PriorityQueue()

        self.reg_numbers = {
           'REG_VIN': 0,
           'REG_VOUT0': 1,
           'REG_VOUT1': 2,
           'REG_IOUT0': 3,
           'REG_IOUT1': 4,
           'REG_WDOG_MASK': 5,
           'REG_OUTPUT': 6,
           'REG_TIMER': 7,
        }

        self.r.setWord(self.reg_numbers['REG_TIMER'],60)
        self.r.setWord(self.reg_numbers['REG_OUTPUT'],0xffff)
        self.device_status = {
            'count': 0,
            'registers': {
                'REG_VIN': {},
                'REG_VOUT0': {},
                'REG_VOUT1': {},
                'REG_OUTPUT': {},
                'REG_WDOG_MASK': {},
                'REG_TIMER': {},
            }
        }


    def resetTimer(self,tval):
        self.q.put_nowait((0,'write','REG_TIMER',tval,None))
        return { 'result': 'OK' }

    def setOutput(self,setval,setmsk):
        self.q.put_nowait((1,'write','REG_OUTPUT',setval,setmsk))
        return { 'result': 'OK' }

    def setResetMask(self,setval,setmsk):
        self.q.put_nowait((2,'write','REG_WDOG_MASK',setval,setmsk))
        return { 'result': 'OK' }

    def printHex(self,v):
        print("val: 0x{:04x}, cmd: 0x{:04x}".format(v['val'],v['cmd']))

    @asyncio.coroutine
    def queueFiller(self):
        keep_running = True
        while keep_running:
            try:
                if self.q.empty():
                    x = (10,'readall')
                    self.q.put_nowait(x)
            except Exception as e:
                print('Exception is Rigminder.queueFiller')
                print(e)
            yield from asyncio.sleep(0.250)

    def doUpdateAll(self):
        rv = self.r.readall()
        if rv is not None:
            for reg_name in self.reg_numbers:
                reg_number = self.reg_numbers[reg_name]
                reg_value = rv[reg_number]
                self.device_status['registers'][reg_name] = {
                    'value': rv[reg_number],
                    'last_update': datetime.datetime.now(),
                }

    @asyncio.coroutine
    def queueHandler(self):
        keep_running = True
        print('handleCommands()') 
        while keep_running:
            while True:
                try:
                    qi = yield from self.q.get()
                    # print(qi)
                    if qi[1] == 'readall':
                        self.doUpdateAll()

                    elif qi[1] == 'write':
                        reg_name = qi[2]
                        reg_val = qi[3]

                        new_val = reg_val
                        if len(qi) == 5:
                            reg_msk = qi[4]
                        if reg_msk is not None:
                            old_val = self.device_status['registers'][reg_name].get('value',0)
                            new_val = old_val & ~reg_msk
                            new_val |= reg_val & reg_msk
                        self.r.setWord(self.reg_numbers[reg_name],new_val)
                        self.doUpdateAll()
                except Exception as e:
                    print('Exception in Rigminder.queueHandler')
                    print(e)

                yield from asyncio.sleep(0.05)
                


 

    def readStatus(self):
        return self.device_status


