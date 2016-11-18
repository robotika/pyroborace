#!/usr/bin/python
"""
  Parse track XML data
  usage:
     ./track.py <xml data>
"""

import math
import sys
from xml.dom.minidom import parse, Node


class Segment:

    @classmethod
    def from_xml(cls, ele):
        name = ele.getAttribute('name')
        seg_type = None
        length = None
        arc = None
        radius = None
        end_radius = None
        for attr in ele.childNodes:
            if attr.nodeType == Node.ELEMENT_NODE:
                if attr.getAttribute('name') == 'type':
                    seg_type = attr.getAttribute('val')
                if attr.getAttribute('name') == 'arc':
                    assert attr.getAttribute('unit') == 'deg', attr.getAttribute('unit')
                    arc = math.radians(float(attr.getAttribute('val')))
                if attr.getAttribute('name') == 'radius':
                    assert attr.getAttribute('unit') == 'm', attr.getAttribute('unit')
                    radius = float(attr.getAttribute('val'))
                if attr.getAttribute('name') == 'end radius':
                    assert attr.getAttribute('unit') == 'm', attr.getAttribute('unit')
                    end_radius = float(attr.getAttribute('val'))
                if attr.getAttribute('name') == 'lg':
                    assert attr.getAttribute('unit') == 'm', attr.getAttribute('unit')
                    length = float(attr.getAttribute('val'))

        assert seg_type in ['lft', 'str', 'rgt'], seg_type
        if seg_type == 'rgt':
            arc = -arc
        return Segment(name, length, arc, radius, end_radius)

    def __init__(self, name=None, length=None, arc=None, radius=None,
                 end_radius=None):
        self.name = name
        self.length = length
        self.arc = arc
        self.radius = radius
        self.end_radius = end_radius

    def __str__(self):
        return "Segment('{}', {}, {}, {})".format(self.name, self.length,
                                                  self.arc, self.radius)

    def nearest(self, x, y):
        """Return signed distance from this segment

        Distance is positive to the left side.
        In case of (x,y) outside the segment "influence"
        return None"""

        # TODO variable turns
        if self.length is not None:
            # line
            if 0 <= x <= self.length:
                return y
            return None

        if self.arc > 0:
            # radius - distance from Point(0, radius)
            if 0 <= math.atan2(x, self.radius - y) <= self.arc:
                return self.radius - math.hypot(x, y - self.radius)
            return None

        # radius - distance from Point(0, -radius)
        if 0 <= -math.atan2(-x, y + self.radius) <= -self.arc:
            return math.hypot(x, y + self.radius) - self.radius
        return None

    def _step(self):
        if self.arc is None:
            # straight segment
            assert self.length is not None
            return self.length, 0.0, 0.0

        assert self.arc is not None
        assert self.radius is not None
        if self.end_radius is None:
            # turn of fixed radius
            angle = self.arc / 2.0
            dist = 2.0 * self.radius * abs(math.sin(self.arc/2.0))
        else:
            # variable radius turn
            # cosine theorem
            dist = math.sqrt(self.radius**2 + self.end_radius**2
                    - 2.0 * math.cos(self.arc) * self.radius  * self.end_radius)
            angle = math.acos((self.radius**2 + dist**2 - self.end_radius**2)/
                              (2.0 * self.radius * dist))
            angle = math.pi/2.0 - angle
            if self.arc < 0:
                angle = -angle
        
        return math.cos(angle)*dist, math.sin(angle)*dist, self.arc

    def step(self, pose=None):
        dx, dy, dh = self._step()
        if pose is None:
            return dx, dy, dh
        x, y, heading = pose
        x += math.cos(heading)*dx - math.sin(heading)*dy
        y += math.sin(heading)*dx + math.cos(heading)*dy
        heading += dh
        return x, y, heading


def get_main_track(xmldoc):
    for section in xmldoc.getElementsByTagName('section'):
        if section.getAttribute('name') == 'Track Segments':
            return section
    return None


def get_track_width(xmldoc):
    for section in xmldoc.getElementsByTagName('section'):
        if section.getAttribute('name') == 'Main Track':
            # search for <attnum name="width" unit="m" val="13"/>
            for attnum in section.getElementsByTagName('attnum'):
                if attnum.getAttribute('name') == 'width':
                    return float(attnum.getAttribute('val'))
    return None


def print_track(track):
    angle = 0.0
    length = 0.0
    for segment in track:
        if segment.arc is not None:
            angle += segment.arc
        if segment.length is not None:
            length += segment.length
        else:
            length += segment.arc * segment.radius
            # TODO variable turns
        print segment.name
    print
    print math.degrees(angle), length


def track2xy(track):
    x, y, heading = (0, 0, 0)
    minx, miny = 0.0, 0.0
    for segment in track:
        x, y, heading = segment.step((x, y, heading))
        print segment.name, x, y, math.degrees(heading)
        minx, miny = min(minx, x), min(miny, y)
    return minx, miny


class Track:
    """Definition of race track"""

    @staticmethod
    def from_xml_file(filename):
        xmldoc = parse(filename)
        segments = []
        for section in get_main_track(xmldoc).childNodes:
            if section.nodeType == Node.ELEMENT_NODE:
                segments.append(Segment.from_xml(section))

        width = get_track_width(xmldoc)
        return Track(segments, width)

    def __init__(self, segments, width):
        self.segments = segments
        self.width = width

    def nearest_segment(self, pose):
        """Find nearest segment on the track"""
        global_x, global_y, global_a = pose
        track_pose = 0, 0, 0
        for segment in self.segments:
            # convert global (x,y) into pose relative coordinates
            x, y, a = track_pose
            ca, sa = math.cos(-a), math.sin(-a)  # rotate back
            sx = global_x - x
            sy = global_y - y
            sx, sy = ca*sx - sa*sy, sa*sx + ca*sy
            dist = segment.nearest(sx, sy)
            if dist is not None:
                if abs(dist) < self.width/2.0:
                    return segment, (sx, sy, global_a - a)
            track_pose = segment.step(track_pose)
        return None, None

    def nearest(self, global_x, global_y):
        segment, rel_pose = self.nearest_segment((global_x, global_y, 0.0))
        if segment is None:
            assert rel_pose is None, rel_pose
            return None
        assert rel_pose is not None
        sx, sy, sa = rel_pose
        dist = segment.nearest(sx, sy)
        assert dist is not None
        assert abs(dist) < self.width/2.0, (abs(dist), self.width)
        return dist


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
    track = Track.from_xml_file(sys.argv[1])
    print_track(track.segments)
    print track2xy(track.segments)

# vim: expandtab sw=4 ts=4 

