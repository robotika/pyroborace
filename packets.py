"""
  Interpretation of I/O UDP packets
  usage:
     python packets.py <logfile>
"""
import math
from struct import unpack_from
import sys

from iolog import packet_gen, INPUT, OUTPUT


class Command(object):
    """Represent command packet for car control"""
    
    @staticmethod
    def from_packet(packet):
        assert len(packet) == 18, len(packet)
        steering, acc, brake = unpack_from('fff', packet, 0)
        return Command(steering, acc, brake)

    def __init__(self, steering, acc, brake):
        self.steering = steering
        self.acc = acc
        self.brake = brake

    def __str__(self):
        return 'Command(steering={}, acc={}, brake={})'.format(
            self.steering, self.acc, self.brake)


class Sensors(object):

    SIMULATION_STOPPED = 5

    @staticmethod
    def from_packet(packet):
        assert len(packet) == 794, len(packet)
        time, dist = unpack_from('ff', packet, 0)
        pos3d = unpack_from('fff', packet, 44)
        vel3d = unpack_from('fff', packet, 80)
        sim_status = unpack_from('B', packet, 792)[0]
        return Sensors(time, dist, pos3d, vel3d, sim_status)

    def __init__(self, time, dist, pos3d, vel3d, sim_status):
        self.time = time
        self.dist = dist
        self.pos3d = pos3d
        self.vel3d = vel3d
        self.sim_status = sim_status

    def speed(self):
        return math.sqrt(sum([x*x for x in self.vel3d]))

    def __str__(self):
        return 'Sensors(time={}, dist={}, pos={}, vel={})'.format(
                self.time, self.dist, self.pos3d, self.vel3d)


def sensors_gen(filename):
    for io_dir, packet in packet_gen(filename):
        if io_dir == INPUT:
            sensors = Sensors.from_packet(packet)
            if sensors.sim_status != Sensors.SIMULATION_STOPPED:
                yield sensors


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)

    for io_dir, packet in packet_gen(sys.argv[1]):
        if io_dir == INPUT:
            obj = Sensors.from_packet(packet)
        elif io_dir == OUTPUT:
            obj = Command.from_packet(packet)
        else:
            assert 0, io_dir  # unsuported type
        print(obj)

# vim: expandtab sw=4 ts=4
