"""
  follow the race loop

  usage:
     demo.py <track XML file>
"""

import math
import socket
import struct
import sys

from track import Track

def segment_turn(segment):
    """Return turn angle in degrees (expected car structure input)"""
    # for Robocar with following definition
    # <section name="Front Axle">
    #   <attnum name="xpos" min="0.1" max="5" val="1.104"/>
    # <section name="Rear Axle">
    #   <attnum name="xpos" min="-5" max="-0.1" val="-1.469"/>
    axis_dist = 1.104 + 1.469

    if segment.arc is None:
        return 0.0
    angle = math.atan2(axis_dist, segment.radius)
    if segment.arc < 0:
        # right left
        angle = -angle
    return math.degrees(angle)


def drive(track, offset):
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = 4001
    soc.bind(('', port))
    soc.settimeout(1.0)
    ctr = 0
    start_position = None
    gas = 0.0
    brake = 0.0
    turn = 0.0
    prev_segment = None
    while True:
        data = struct.pack('fffiBB', turn, gas, brake, 1, 11, ctr & 0xFF)
        soc.sendto(data, ('127.0.0.1', 3001))
        try:
            status = soc.recv(1024)
            assert len(status) == 794, len(status)
            absPosX, absPosY, absPosZ = struct.unpack_from('fff', status, 44)
            angX, angY, angZ = struct.unpack_from('fff', status, 56)
            num_cars = struct.unpack_from('B', status, 128)
            posX = struct.unpack_from('f', status, 168)[0]
            posY = struct.unpack_from('f', status, 324)[0]
            speed = struct.unpack_from('f', status, 480)[0]
            x = absPosX - offset[0]
            y = absPosY - offset[1]
            heading = angZ  # in radiands +/- PI
            segment, rel_pose = track.nearest_segment((x, y, heading))
            if segment is not None:
                signed_dist, heading_offset = segment.get_offset(rel_pose)
                if signed_dist < 5.0:
                    gas = 0.2
                else:
                    gas = 0.1

                turn = segment_turn(segment)
                if heading_offset is not None:
                    turn -= math.degrees(heading_offset)
                if signed_dist < -1.0:
                    turn += min(1.0, -1.0 - signed_dist)
                elif signed_dist > 1.0:
                    # turn right
                    turn += max(-1.0, 1.0 - signed_dist)  
            if prev_segment != segment:
                print segment, rel_pose
                prev_segment = segment

        except socket.timeout:
            pass
        ctr += 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
    filename = sys.argv[1]
    track = Track.from_xml_file(filename)
    track.width = 100  # extra margin
    assert filename.endswith('espie.xml')  # otherwise not defined offset
    offset = 0, 0
    drive(track, offset)

# vim: expandtab sw=4 ts=4
