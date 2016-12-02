import unittest
import math
from xml.dom.minidom import parseString

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

    def test_variable_turn_offset(self):
        arc = Segment(arc=math.radians(90), radius=10.0, end_radius=20.0)
        self.assertEqual(arc.get_offset((0, 0, 0)), (0, 0))
        self.assertEqual(arc.get_offset((20, 10, math.radians(90))), (0, 0))

        arc = Segment(arc=math.radians(-90), radius=10.0, end_radius=20.0)
        self.assertEqual(arc.get_offset((0, 0, 0)), (0, 0))
        self.assertEqual(arc.get_offset((20, -10, math.radians(-90))), (0, 0))

    def test_segment_str(self):
        s = Segment(name='s11', length=10)
        self.assertEqual(str(s), "Segment('s11', 10, None, None)")

    def test_from_xml(self):
        xmldoc = parseString("""
      <section name="s6">
        <attstr name="type" val="lft" />
        <attnum name="arc" unit="deg" val="102.0" />
        <attnum name="radius" unit="m" val="32.7" />
        <attnum name="end radius" unit="m" val="38.4" />
        <attnum name="grade" unit="%" val="-3.0" />
        <attnum name="profil end tangent" unit="%" val="-3.0" />
        <attnum name="profil steps length" unit="m" val="4.0" />
        <attnum name="banking start" unit="deg" val="0.0"/>
        <attnum name="banking end" unit="deg" val="-4.0"/>
        <attstr name="marks" val="50;100;150"/>
        <section name="Left Border">
          <attnum name="width" unit="m" val="1.0" />
          <attnum name="height" unit="m" val="0.05" />
          <attstr name="surface" val="curb-left" />
          <attstr name="style" val="curb" />
        </section>
        <section name="Left Side">
          <attnum name="start width" unit="m" val="10.0" />
          <attnum name="end width" unit="m" val="12.0" />
          <attstr name="surface" val="dirtA" />
        </section>
        <section name="Right Side">
          <attnum name="start width" unit="m" val="32.0" />
          <attnum name="end width" unit="m" val="40.0" />
          <attstr name="surface" val="sand" />
        </section>
      </section>
""")
        s = Segment.from_xml(xmldoc.childNodes[0])
        self.assertEqual(s.name, 's6')
        self.assertIsNone(s.length)
        self.assertAlmostEqual(math.degrees(s.arc), 102.0)
        self.assertAlmostEqual(s.radius, 32.7)
        self.assertAlmostEqual(s.end_radius, 38.4)
        self.assertAlmostEqual(s.profil_steps_length, 4.0)

# vim: expandtab sw=4 ts=4
