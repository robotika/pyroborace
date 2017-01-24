import unittest
import math

from packets import Command

class PacketsTest(unittest.TestCase):

    def test_command_from_packet(self):
        packet = b'\xce\x9d\x04\xc0\xcd\xccL>\x00\x00\x00\x00\x01\x00\x00\x00\x0b\x01'
        cmd = Command.from_packet(packet)
        self.assertAlmostEqual(cmd.acc, 0.2)

# vim: expandtab sw=4 ts=4
