# simplest version = just go straight with 50% gas

import socket
import struct

soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ctr = 0
while True:
    data = struct.pack('fffiBB', 0, 0.5, 0, 1, 11, ctr & 0xFF)
    soc.sendto(data, ('127.0.0.1', 3001))
    ctr += 1
