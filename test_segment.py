import unittest
import math

from segment import Segment

class SegmentTest(unittest.TestCase):

    def test_stright_step(self):
        s = Segment(length=10.0)
        x, y, heading = s.step()
        self.assertAlmostEqual(x, 10.0)
        self.assertAlmostEqual(y, 0.0)
        self.assertAlmostEqual(heading, 0.0)

    def test_turn_step(self):
        s = Segment(arc=math.radians(90.0), radius=5.0)
        x, y, heading = s.step()
        self.assertAlmostEqual(x, 5.0)
        self.assertAlmostEqual(y, 5.0)
        self.assertAlmostEqual(heading, math.radians(90.0))

        s = Segment(arc=math.radians(-90.0), radius=5.0)
        x, y, heading = s.step()
        self.assertAlmostEqual(x, 5.0)
        self.assertAlmostEqual(y, -5.0)
        self.assertAlmostEqual(heading, math.radians(-90.0))

    def test_variable_turn_step(self):
        s = Segment(arc=math.radians(90.0), radius=5.0, end_radius=6.0)
        x, y, heading = s.step()
        self.assertAlmostEqual(x, 6.0)
        self.assertAlmostEqual(y, 5.0)
        self.assertAlmostEqual(heading, math.radians(90.0))

        s1 = Segment(arc=1.23, radius=10.0)
        s2 = Segment(arc=1.23, radius=10.0, end_radius=10.0)
        for a, b in zip(s1.step(), s2.step()):
            self.assertAlmostEqual(a, b)

    def test_corkscrew_s10_step(self):
        s = Segment(arc=math.radians(-27.0), radius=105.7, end_radius=422.8)
        x, y, heading = s.step()
        self.assertAlmostEqual(x, 191.94718328988037)
        self.assertAlmostEqual(y, 271.0175584268419)  # this is wrong
        self.assertAlmostEqual(heading, math.radians(-27.0))

    def test_line_offset(self):
        line = Segment(length=30.0)
        self.assertEqual(line.get_offset((3.0, 4.0, 0)), (4.0, 0))
        self.assertEqual(line.get_offset((33.0, 4.0, 0)), (None, None))
        self.assertEqual(line.get_offset((5.0, -2.0, 0.1)), (-2.0, 0.1))

    def test_arc_offset(self):
        arc = Segment(arc=math.radians(90), radius=10.0)
        self.assertEqual(arc.get_offset((0, 0, 0)), (0, 0))
        self.assertEqual(arc.get_offset((10, 0, 0)),
                (-(math.sqrt(2)*10 - 10), math.radians(-45)))
        self.assertEqual(arc.get_offset((-1, 0, 0)), (None, None))
        self.assertEqual(arc.get_offset((11, 11, 0)), (None, None))

        arc = Segment(arc=math.radians(-90), radius=10.0)
        self.assertEqual(arc.get_offset((0, 0, 0))[0], 0)
        self.assertEqual(arc.get_offset((10, 0, 0))[0], math.sqrt(2)*10 - 10)
        self.assertEqual(arc.get_offset((-1, 0, 0))[0], None)

    def test_segment_str(self):
        s = Segment(name='s11', length=10)
        self.assertEqual(str(s), "Segment('s11', 10, None, None)")

# vim: expandtab sw=4 ts=4