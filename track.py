#!/usr/bin/python
"""
  Parse track XML data
  usage:
     ./track.py <xml data>
"""

import math
import sys
from xml.dom.minidom import parse, Node

from segment import Segment


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
            dist = segment.get_offset((sx, sy, global_a - a))[0]
            if dist is not None:
                if abs(dist) < self.width/2.0:
                    return segment, (sx, sy, global_a - a)
            track_pose = segment.step(track_pose)
        return None, None

    def get_offset(self, pose):
        segment, rel_pose = self.nearest_segment(pose)
        if segment is None:
            assert rel_pose is None, rel_pose
            return None, None
        assert rel_pose is not None
        dist, diff_heading = segment.get_offset(rel_pose)
        assert dist is not None
        assert abs(dist) < self.width/2.0, (abs(dist), self.width)
        return dist, diff_heading


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
    track = Track.from_xml_file(sys.argv[1])
    print_track(track.segments)
    print track2xy(track.segments)

# vim: expandtab sw=4 ts=4 

