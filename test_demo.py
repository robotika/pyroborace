import unittest
import math

from demo import segment_turn
from track import Segment

class DemoTest(unittest.TestCase):

    def test_segment_turn(self):
        s = Segment(name='t1', radius=66.6, arc=-28.0)
        self.assertAlmostEqual(segment_turn(s), -2.212, places=2)

        s = Segment(name='t4', radius=53.3, arc=-110.0)
        self.assertAlmostEqual(segment_turn(s), -2.763, places=2)

# vim: expandtab sw=4 ts=4
