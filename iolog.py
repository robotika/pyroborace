"""
  Input/Output logging
"""

from datetime import datetime
import os
import socket
from struct import pack, unpack


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


class IOFromFile(object):

    def __init__(self, filename):
        self.f = open(filename, 'rb')
        data = self.f.read(8)
        assert unpack('II', data) == (MAGIC_HEADER, VERSION)

    def bind(self, address):
        pass

    def settimeout(self, value):
        pass

    def sendto(self, data, address):
        length, io_dir = unpack('HH', self.f.read(4))
        assert io_dir == OUTPUT
        ref_data = self.f.read(length - 2)
        assert data == ref_data

    def recv(self, bufsize):
        length, io_dir = unpack('HH', self.f.read(4))
        assert io_dir == INPUT
        assert length - 2 <= bufsize
        return self.f.read(length - 2)


def packet_gen(filename):
    f = open(filename, 'rb')
    data = f.read(8)
    assert unpack('II', data) == (MAGIC_HEADER, VERSION)
    while True:
        data = f.read(4)
        if len(data) != 4:
            break  # EOF

        length, io_dir = unpack('HH', data)
        yield io_dir, f.read(length - 2)

# vim: expandtab sw=4 ts=4
