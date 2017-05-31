
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import json
import random
import sys
import os
import string
from urllib.parse import urlparse
from urllib.parse import parse_qs
import re

PORT = 8004

MAX_QUERY_LEN = 60 * 1024

def killAll(name):
    s = 'taskkill /f /im "' + name + '" /T'
    os.system(s)
    print(s)

def taskStart(path):
    print("Starting " + path)
    os.startfile(path)



class myHandler(BaseHTTPRequestHandler):

    BaseHTTPRequestHandler.fileconfig = {
        '/index.html':    ('text/html',              'static/index.html'),
        '/top.js':        ('application/javascript', 'static/top.js'),
        '/':              ('text/html',              'static/index.html'),
    }
    BaseHTTPRequestHandler.filecache= {
    }

    def send_resp(self, rcode, odata):
        mimetype = 'application/json'
        self.send_response(rcode)
        self.send_header('Content-Type',mimetype)
        self.end_headers()
        self.wfile.write(bytes(json.dumps(odata),'utf-8'))
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
            data = {}
            if content_len < self.server.ctx['max_query_len']:
                post_body = self.rfile.read(content_len).decode('utf-8')
                data = json.loads(post_body)
            return data

        except Exception as e:
            print('Could not get post body')
            print(e)
            return {}


    def do_GET(self):

        odata = { 'result': 'FAIL' }
        rcode = 500 

        pathlen = len(self.path)
        if pathlen <= 0 or pathlen > self.server.ctx['max_query_len']:
            self.send_resp(rcode, odata)
            return

        try:
            up = urlparse(self.path)
            if not isinstance(up, tuple):
                print('urlparse failed')
                self.send_resp(rcode, odata)
                return

            if len(up.path) == 0 or len(up.path) > self.server.ctx['max_query_len']:
                self.send_resp(rcode, odata)
                print('no path or path too long')
                return

            if up.path in self.fileconfig:
                return self.splatFile(self.fileconfig[up.path][0],self.fileconfig[up.path][1])

            if up.path == '/gettoken':
                odata['result'] = 'OK'
                self.server.genSessID()
                odata['token'] = self.server.ctx['sessID']
                rcode = 200
                self.send_resp(rcode, odata)
                return


        except Exception as e:
            print('exception handling get')
            print(repr(e))

        self.send_resp(rcode, odata)
        return





        self.server.genSessID()
        odata['sessID'] = self.server.ctx['sessID']

        self.send_resp(rcode, odata)

    def do_POST(self):

        odata = { 'result': 'FAIL' }
        rcode = 500

        pathlen = len(self.path)
        if pathlen <= 0 or pathlen > self.server.ctx['max_query_len']:
            self.send_resp(rcode, odata)
            return

        try:
            up = urlparse(self.path)
            if not isinstance(up, tuple):
                print('urlparse failed')
                self.send_resp(rcode, odata)
                return

            if len(up.path) == 0 or len(up.path) > self.server.ctx['max_query_len']:
                self.send_resp(rcode, odata)
                return

            args = self.getMessage()

            if up.path == '/killit':
                tok = args.get('token',None)
                secret = args.get('secret',None)
                if tok == self.server.ctx['sessID'] and secret == self.server.ctx['secret']:
                    rcode = 200
                    odata = { 'result': 'OK', 'msg': 'weapon discharged' }
                    killAll('RemoteUty.exe')
                else:
                    pass

            if up.path == '/startit':
                tok = args.get('token',None)
                secret = args.get('secret',None)
                if tok == self.server.ctx['sessID'] and secret == self.server.ctx['secret']:
                    rcode = 200
                    odata = { 'result': 'OK', 'msg': 'start attempted' }
                    taskStart("C:\Program Files (x86)\Icom\RS-BA1\RemoteUtility\RemoteUty.exe")
                else:
                    pass

        except Exception as e:
            print('POST exception')
            print(repr(e))

        self.send_resp(rcode, odata)
        return



def start_server(port, handler, ctx):
    keep_going = True 
    while keep_going:
        keep_going = False 
        try:
            class MyServer(HTTPServer):
                def __init__(self, *args, **kw):
                    HTTPServer.__init__(self, *args, **kw)
                    self.ctx = ctx
                def genSessID(self):
                    self.ctx['sessID'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))

            server = MyServer(('', port), handler)
            print("serving at port: ", port)
            server.serve_forever()
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            keep_going = False
            server.socket_close()
            sys.exit()
        except Exception as e:
            print(repr(e))
            print('Something happened, restarting')
            try:
                server.socket_close()
            except Exception as f:
                pass


if __name__ == '__main__':
    args = {
        'max_query_len': 64 * 1024,
        'secret': 'Beeblebrox',
    } 
    start_server(8004, myHandler, args)

