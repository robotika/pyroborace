"""
  Input/Output logging
"""

import socket


class Timeout(socket.timeout):
    pass


class IOLog(object):

    def __init__(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def bind(self, address):
        self.soc.bind(address)

    def settimeout(self, value):
        self.soc.settimeout(value)

    def sendto(self, data, address):
        try:
            self.soc.sendto(data, address)
        except socket.timeout as e:
            raise Timeout(e)

    def recv(self, bufsize):
        try:
            return self.soc.recv(bufsize)
        except socket.timeout as e:
            raise Timeout(e)

# vim: expandtab sw=4 ts=4
