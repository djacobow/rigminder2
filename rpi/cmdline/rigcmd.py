#!/usr/bin/env python3

import sys
import re
import json
import argparse

import rigmi2c

class Device:
    def __init__(self):
        self.r = rigmi2c.rigmi2c()
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
        self.bitmasks = {
            'dc0': 0x1,
            'dc1': 0x2,
            'oc0': 0x4,
            'oc1': 0x8,
        }

    def setReg(self, regname, value):
        self.r.setWord(self.reg_numbers[regname], value)

    def setBits(self, regname, value):
        rn = self.reg_numbers[regname]
        ov = self.getAll()[regname]
        ov |= value
        self.r.setWord(rn, ov)

    def clrBits(self, regname, value):
        rn = self.reg_numbers[regname]
        ov = self.getAll()[regname]
        ov &= ~value
        self.r.setWord(rn, ov)

    def getAll(self):
        rv = self.r.readall()
        if rv is not None:
            return { n:rv[self.reg_numbers[n]] for n in self.reg_numbers }
        return None

    def showOutputs(self, regdata):
        oss = ['Outputs:']
        for n in self.bitmasks:
            outdata  = regdata['REG_OUTPUT']
            maskdata = regdata['REG_WDOG_MASK']
            bm = self.bitmasks[n]
            is_on = outdata & bm
            is_wdog_enabled = maskdata & bm
            oss.append('    {} is {}. {}'.format(
                n,
                "on" if is_on else "off",
                "watchdog enabled" if is_wdog_enabled else ""
            ))
        return '\n'.join(oss)


    def handleCommands(self, args):
        def makeBM(l):
            bm = 0
            for n in l:
                bm |= self.bitmasks[n]
            return bm

        if args.dogall:
            self.setReg('REG_WDOG_MASK',0xffff)
        if args.dogoff:
            self.setReg('REG_WDOG_MASK',0)
        if args.timer:
            self.setReg('REG_TIMER',args.timer[0])
        if args.dogset is not None:
            self.setBits('REG_WDOG_MASK',makeBM(args.dogset))
        if args.dogclear is not None:
            self.clrBits('REG_WDOG_MASK',makeBM(args.dogclear))
        if args.on is not None:
            self.setBits('REG_OUTPUT',makeBM(args.on))
        if args.off is not None:
            self.clrBits('REG_OUTPUT',makeBM(args.off))

    def getArgs2(self):
        switches = ('dc0','dc1','oc0','oc1')
        parser = argparse.ArgumentParser(prog='rigcmd.py',
                description='A command line utility to control a rigminder2')
        parser.add_argument('-on', nargs='+', choices=switches,
                            help='Turn output on')
        parser.add_argument('-off',nargs='+', choices=switches,
                            help='Turn output off')
        parser.add_argument('-timer', nargs=1, type=int,
                            help='Reset the watchdog timer to n seconds')
        parser.add_argument('-dogset',nargs='+', choices=switches,
                            help='Allow watchdog to turn off the following')
        parser.add_argument('-dogclear',nargs='+', choices=switches,
                            help='Disallow watchdog from turning off these')
        parser.add_argument('-dogoff',action='store_true',
                            help='Disable watchdog timer entirely')
        parser.add_argument('-dogall',action='store_true',
                            help='Enable watchdog timer on all outputs')
        r = parser.parse_args()
        print('r',r)
        return r


if __name__ == '__main__':
    d = Device()
    args     = d.getArgs2()
    d.handleCommands(args)
    result = d.getAll()
    print(d.showOutputs(result))
    print(json.dumps(result,sort_keys=True, indent=2))

