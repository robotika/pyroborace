import math
import sys
from xml.dom.minidom import parse, Node


def normalize_angle(angle):
    """angle in radians, return in range -PI .. PI"""
    while angle < -math.pi:
        angle += 2*math.pi
    while angle > math.pi:
        angle -= 2*math.pi
    return angle 


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

    def get_offset(self, pose):
        """Calculate offset from the segment.

        pose is segment relative position
        (the segment starts at (0, 0, 0))
        
        Return signed distance offset and heading offset

        Distance is positive to the left side.
        In case of (x,y) outside the segment "influence"
        return None"""

        x, y, heading = pose

        # TODO variable turns
        if self.length is not None:
            # line
            if 0 <= x <= self.length:
                return y, normalize_angle(heading)
            return None, None

        if self.arc > 0:
            # radius - distance from Point(0, radius)
            angle = math.atan2(x, self.radius - y)
            if 0 <= angle <= self.arc:
                return (self.radius - math.hypot(x, y - self.radius),
                        normalize_angle(heading - angle))
            return None, None

        # radius - distance from Point(0, -radius)
        angle = -math.atan2(-x, y + self.radius)
        if 0 <= angle <= -self.arc:
            return (math.hypot(x, y + self.radius) - self.radius,
                    normalize_angle(heading + angle))
        return None, None

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

# vim: expandtab sw=4 ts=4
