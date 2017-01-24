#!/usr/bin/python
"""
  Parse track XML data
  usage:
     ./track.py <xml data>
"""

import math
import os
import sys
from xml.dom.minidom import parse, Node

from segment import Segment


def get_main_track(xmldoc):
    for section in xmldoc.getElementsByTagName('section'):
        if section.getAttribute('name') == 'Track Segments':
            return section
    return None


def get_track_root_info(xmldoc, name):
    assert name in ['width', 'profil steps length'], name
    for section in xmldoc.getElementsByTagName('section'):
        if section.getAttribute('name') == 'Main Track':
            # search for <attnum name="width" unit="m" val="13"/>
            for attnum in section.getElementsByTagName('attnum'):
                if attnum.getAttribute('name') == name:
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
        print(segment.name)
    print()
    print(math.degrees(angle), length)


def track2xy(track):
    x, y, heading = (0, 0, 0)
    minx, miny = 0.0, 0.0
    for segment in track:
        x, y, heading = segment.step((x, y, heading))
    return x, y, heading


class Track:
    """Definition of race track"""

    @staticmethod
    def from_xml_file(filename):
        xmldoc = parse(filename)
        width = get_track_root_info(xmldoc, 'width')
        default_profil_steps_length = get_track_root_info(xmldoc, 'profil steps length')

        segments = []
        for section in get_main_track(xmldoc).childNodes:
            if section.nodeType == Node.ELEMENT_NODE:
                s = Segment.from_xml(section)
                if s.end_radius is None:
                    segments.append(s)
                else:
                    profil_steps_length = default_profil_steps_length
                    if s.profil_steps_length is not None:
                        profil_steps_length = s.profil_steps_length
                    length = abs((s.radius + s.end_radius)/2.0 * s.arc)
                    num_steps = int(length/profil_steps_length) + 1
                    if num_steps == 1:
                        segments.append(s)
                    else:
                        # rearange steps so:
                        #  - every part of the turn has the same length
                        #  - the first part has curvature given by ``radius``
                        #  - the last part had curvature given by ``end_radius``
                        #  - there are ``steps`` parts
                        #  - the total ``arc`` angle does not change
                        dradius = (s.end_radius - s.radius)/float(num_steps - 1)

                        tmp = 0.0
                        for i in xrange(num_steps):
                            tmp += 1.0/(s.radius + i*dradius)
                        geom_average = 1.0 / tmp

                        for i in xrange(num_steps):
                            name = s.name + '.' + str(i)
                            radius = s.radius + i*dradius
                            arc = s.arc * geom_average / radius
                            segments.append(Segment(name=name, arc=arc,
                                                    radius=radius,
                                                    end_radius=None))

        return Track(segments, width)

    def __init__(self, segments, width):
        self.segments = segments
        self.width = width

    def nearest_segment(self, pose):
        """Find nearest segment on the track
        
        Return segment and relative pose to the segment

        This method can return (None, None) when:
        - there is no segment in the ``Track.segments``
        - the ``pose`` is outside of the scope for each
          segment

        For the valid closed loop track you should always get values
        other than (None, None).        
        """
        global_x, global_y, global_a = pose
        track_pose = 0, 0, 0
        best = None, None
        best_dist = None
        for segment in self.segments:
            # convert global (x,y) into pose relative coordinates
            x, y, a = track_pose
            ca, sa = math.cos(-a), math.sin(-a)  # rotate back
            sx = global_x - x
            sy = global_y - y
            sx, sy = ca*sx - sa*sy, sa*sx + ca*sy
            dist = segment.get_offset((sx, sy, global_a - a))[0]
            if dist is not None:
                if best_dist is None or abs(dist) < best_dist:
                    best = segment, (sx, sy, global_a - a)
                    best_dist = abs(dist)
            track_pose = segment.step(track_pose)
        return best

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
        print(__doc__)
        sys.exit(2)
    path = sys.argv[1]
    if path.endswith('xml'):
        print(path)
        track = Track.from_xml_file(path)
        print(track2xy(track.segments))
    else:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith('xml'):
                    track = Track.from_xml_file(os.path.join(dirpath, filename))
                    end_pose = track2xy(track.segments)
                    print(filename, end_pose)
                    assert abs(end_pose[0]) + abs(end_pose[1]) < 0.5, end_pose
                    deg_angle = int(round(math.degrees(end_pose[2])))
                    assert deg_angle in [-360, 0, 360], deg_angle

# vim: expandtab sw=4 ts=4 

