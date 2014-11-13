#!/usr/bin/env python

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading

from urlparse import urlparse

import os
import sys
import uuid

import Image
import ImageDraw
import ImageFont



class Handler(BaseHTTPRequestHandler):

    def parseEntry(self, filename):
        title = ''
        year = ''
        citations = 0

        with open(filename, 'r') as f:
            for line in f:
                items = line.split()
                if len(items) == 0: continue
                if items[0] == 'Title':
                    title = ' '.join(items[1:-1])
                if items[0] == 'Year':
                    year = int(items[1])
                if items[0] == 'Citations' and items[1] != 'list':
                    citations = int(items[1])

        return [title, year, citations]

    def generateImg(self, entry):
        img = Image.new('RGB', (200, 100))
        d = ImageDraw.Draw(img)

        text1 = entry[0] + ',' + str(entry[1])
        text2 = 'citations: ' + str(entry[2])

        text_width1, text_height1 = d.textsize(text1)
        text_width2, text_height2 = d.textsize(text2)

        img = Image.new('RGB', (text_width1+10*2, text_height1+text_height2+10+10*2), (255,255,255))
        d = ImageDraw.Draw(img)

        font = ImageFont.truetype("Open_Sans/OpenSans-Regular.ttf", 15)

        d.text((10, 10), text1, fill=(0, 0, 0), font=font)
        d.text((10, text_height1+20), text2, fill=(0, 0, 0), font=font)

        img.save('test.png')

    def do_GET(self):

        o = urlparse(self.path)

        print self.path

        if len(o.query) >= 1:
            filename = 'tmp_' + str(uuid.uuid4())
            os.system('./scholar.py -c 1 -p "' + o.query + '" > ' + filename)
            
            entry = self.parseEntry(filename)

            print entry

            self.generateImg(entry)

            os.system('rm ' + filename)    

        self.send_response(200)
        self.end_headers()
        message =  threading.currentThread().getName()
        self.wfile.write(message)
        self.wfile.write('\n')
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == '__main__':
    host = 'localhost'
    port = 8080
    server = ThreadedHTTPServer((host, port), Handler)
    print 'Starting server',  host, ':', port, ' use <Ctrl-C> to stop'
    server.serve_forever()