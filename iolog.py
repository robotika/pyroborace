"""
  Input/Output logging
"""

from datetime import datetime
import os
import socket
from struct import pack


MAGIC_HEADER = 0x492F4F01  # I/O
VERSION = 1

INPUT = 1
OUTPUT = 0


class Timeout(socket.timeout):
    pass


class IOLog(object):

    def __init__(self, prefix):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        if not os.path.exists('logs'):
            os.mkdir('logs')
        filename = datetime.now().strftime('logs/'+prefix+'-%y%m%d_%H%M%S.log')
        self.f = open(filename, 'wb')
        self.f.write(pack('II', MAGIC_HEADER, VERSION))

    def bind(self, address):
        self.soc.bind(address)

    def settimeout(self, value):
        self.soc.settimeout(value)

    def sendto(self, data, address):
        try:
            self.f.write(pack('HH', len(data) + 2, OUTPUT))
            self.f.write(data)
            self.soc.sendto(data, address)
        except socket.timeout as e:
            raise Timeout(e)

    def recv(self, bufsize):
        try:
            data = self.soc.recv(bufsize)
            self.f.write(pack('HH', len(data) + 2, INPUT))
            self.f.write(data)
            return data
        except socket.timeout as e:
            raise Timeout(e)

# vim: expandtab sw=4 ts=4
