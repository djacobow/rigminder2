#!/usr/bin/env python3

import sys
import os
import re
import json
import datetime
from http.server import BaseHTTPRequestHandler,HTTPServer
from urllib.parse import urlparse
from urllib.parse import parse_qs
import time
import asyncio
import itertools
import random
import Rigminder as rm
#import FakeRigminder as rm


MAX_QUERY_LEN = 1024


def call_in_background(target, *, loop=None, executor=None):
    if loop is None:
        loop = asyncio.get_event_loop()
    if callable(target):
        return loop.run_in_executor(executor, target)
    raise TypeError('target must not be callable, not {!r}'.format(type(target)))


class myHandler(BaseHTTPRequestHandler):

    BaseHTTPRequestHandler.fileconfig = {
        '/favicon.ico':   ('image/x-icon',           'static/favicon.ico'),
        '/icon-logo.png': ('image/png',              'static/icon-logo.png'),
        '/index.html':    ('text/html',              'static/index.html'),
        '/top.js':        ('application/javascript', 'static/top.js'),
        '/default.css':   ('text/css',               'static/default.css'),
        '/':              ('text/html',              'static/index.html'),
    }

    BaseHTTPRequestHandler.filecache = {}

    def send_resp(self,rcode,odata):
        mimetype = 'application/json'
        self.send_response(rcode)
        self.send_header('Content-Type',mimetype)
        #self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        self.wfile.write(bytes(json.dumps(odata,default=json_serial),'utf-8'))
        return

    def splatFile(self, mt, fn):
        is_binary = re.search(r'\.(ico|png)$',fn)
        file_mode = 'r'
        if is_binary:
            file_mode = 'rb'

        fdata = None
#        if fn in self.filecache:
        if False:
            fdata = self.filecache[fn]

        else:
            with open(fn,file_mode) as fh:
                fdata = fh.read()
                self.filecache[fn] = fdata

        self.send_response(200)
        self.send_header('Content-Type',mt)
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        if is_binary:
            self.wfile.write(fdata)
        else:
            self.wfile.write(bytes(fdata,'utf-8'))

        return

    def getMessage(self):
        try:
            headers = self.headers
            content_len = int(headers.get('Content-Length',0))
            post_body = self.rfile.read(content_len).decode('utf-8')
            data = json.loads(post_body)
            return data
        except Exception as e:
            print('Could not get post body')
            print(e)
            return {}



    def do_POST(self):
        global MAX_QUERY_LEN
        print('POST')

        odata = { 'result': 'FAIL' }
        rcode = 500

        pathlen = len(self.path)
        if pathlen <= 0 or pathlen > MAX_QUERY_LEN:
            self.send_resp(rcode, odata)
            return

        try:
            up = urlparse(self.path)
            if not isinstance(up, tuple):
                print('-E- Urlparse failed.')
                self.send_resp(rcode,odata)
                return

            if len(up.path) == 0 or len(up.path) > MAX_QUERY_LEN:
                print('-E- No path or too long.')
                self.send_resp(rcode,odata)
                return

            if up.path == '/timer':
                print('/timer')
                args = self.getMessage()
                print(args)
                res = device.resetTimer(int(args['timer_val']))
                res['server_access_time'] = datetime.datetime.now()
                self.send_resp(200,res)
                return

            if up.path == '/setoutput':
                print('/setoutput')
                args = self.getMessage()
                res = device.setOutput(int(args['set_val']))
                res['server_access_time'] = datetime.datetime.now()
                self.send_resp(200,res)
                return

            if up.path == '/setresetmask':
                print('/setresetmask')
                args = self.getMessage()
                res = device.setResetMask(int(args['set_val']))
                res['server_access_time'] = datetime.datetime.now()
                self.send_resp(200,res)
                return

        except Exception as e:
            print('Exception handling POST:')
            print(repr(e))

        self.send_resp(rcode, odata)
        return



    def do_GET(self):
        global MAX_QUERY_LEN

        odata = { 'result': 'FAIL' }
        rcode = 500

        pathlen = len(self.path)
        if pathlen <=0 or pathlen > MAX_QUERY_LEN:
            self.send_resp(rcode, odata)
            return

        try:
            up = urlparse(self.path)
            if not isinstance(up, tuple):
                print('-E- Urlparse failed.')
                self.send_resp(rcode,odata)
                return

            if len(up.path) == 0 or len(up.path) > MAX_QUERY_LEN:
                self.send_resp(rcode,odata)
                print('-E- No path or too long.')

            if up.path in self.fileconfig:
                return self.splatFile(self.fileconfig[up.path][0],self.fileconfig[up.path][1])

            if up.path == '/status':
                status = device.readStatus()
                status['server_access_time'] = datetime.datetime.now()
                self.send_resp(200,status)
                return


        except Exception as e:
            print('Exception handling GET:')
            print(repr(e))

        self.send_resp(rcode, odata)
        return



def keep_server_up(port, handler):
    print('keep_server_up')
    keep_going = True
    while keep_going:
        print('keeping_going')
        try:
            #Create a web server and define the handler to manage the
            #incoming request
            print('create server')
            server = HTTPServer(('', port), handler)
            print('Started httpserver on port ' , port)
    
            #Wait forever for incoming htto requests
            server.serve_forever()
        except KeyboardInterrupt:
            print('^C received, shutting down the web server')
            keep_going = False
            server.socket.close()
        except Exception as e:
            print('Received some other exception')
            print(repr(e))
            print('Will try to restart')
            try:
                server.socket.close()
            except Exception as f:
                pass

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")

def server_wrap():
    try:
        keep_server_up(8003,myHandler)
    except Exception as e:
        print(e)

   

if __name__ == '__main__':
    device = rm.Device()
    loop = asyncio.get_event_loop()
    call_in_background(server_wrap,loop=loop)
    loop.run_until_complete(asyncio.gather(
        device.queueFiller(),
        device.queueHandler(),
    ))
    loop.close()

