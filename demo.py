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


def drive(track):
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = 4001
    soc.bind(('', port))
    soc.settimeout(1.0)
    ctr = 0
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
            heading = angZ  # in radiands +/- PI

            absVelX, absVelY = struct.unpack_from('ff', status, 80)
            prediction_time = 0.5  # sec
            absPosX += prediction_time * absVelX
            absPosY += prediction_time * absVelY

            segment, rel_pose = track.nearest_segment((absPosX, absPosY, heading))
            if segment is not None:
                signed_dist, heading_offset = segment.get_offset(rel_pose)
                if abs(signed_dist) < 5.0:
                    if abs(signed_dist) < 2.0:
                        gas = 0.4
                    else:
                        gas = 0.2
                else:
                    gas = 0.1

                turn = segment_turn(segment)
                if heading_offset is not None:
                    turn -= math.degrees(heading_offset)

                dead_band = 0.1
                max_dist_turn_deg = 10

                if signed_dist < -dead_band:
                    # turn left
                    turn += min(max_dist_turn_deg, -dead_band - signed_dist)

                elif signed_dist > dead_band:
                    # turn right
                    turn += max(-max_dist_turn_deg, dead_band - signed_dist)

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
    drive(track)

# vim: expandtab sw=4 ts=4
