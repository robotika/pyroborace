import unittest
import math

from segment import Segment
from track import Track

class TrackTest(unittest.TestCase):

    def test_track_usage(self):
        line = Segment(length=100.0)
        arc = Segment(arc=math.radians(90), radius=50.0)

        track = Track([line, arc]*4, width = 20)
        self.assertEqual(track.get_offset((0, 0, 0))[0], 0)
        self.assertEqual(track.get_offset((155, 50, 0))[0], -5)
        self.assertEqual(track.get_offset((150, 150, 0))[0], 0)

        arc60 = Segment(arc=math.radians(60), radius=10.0)
        track = Track([line, arc60]*6, width = 20)
        d = math.sqrt(3.0)/2.0
        self.assertAlmostEqual(track.get_offset((100 + 10*d, 5, 0))[0], 0)
        self.assertAlmostEqual(track.get_offset((100 + 10*d + 10, 5 + 20*d, 0))[0], 0)

        segment, pose = track.nearest_segment((0, 0, 0))
        self.assertIsNotNone(segment)
        self.assertAlmostEqual(segment.length, 100.0)

    def test_nearest_segment(self):
        line = Segment(length=100.0)
        arc = Segment(arc=math.radians(180), radius=10.0)

        # note, that width is artifically set to overlap
        track = Track([line, arc]*2, width = 100)
        segment, rel_pose = track.nearest_segment((50, 15, math.radians(180)))
        self.assertIsNone(segment.arc)
        self.assertAlmostEqual(rel_pose[2], 0.0)

# vim: expandtab sw=4 ts=4
