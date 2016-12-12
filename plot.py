#!/usr/bin/python
"""
  Plot track data
  usage:
       ./plot.py <track XML> [<log file> [<log file> ...]]
"""
import sys
from math import sin, cos, pi

import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

from track import Track
from packets import sensors_gen


# Notes:
#
# The arc segments are interpolated via Bezier curves. See
#   http://www.whizkidtech.redprince.net/bezier/circle/
# or
#   http://www.tinaja.com/glib/ellipse4.pdf
# for explanation of recommended scale factors

# Bezier curve - length of control points fro PI/2 circle split
KAPPA = 0.5522847498

def track_border(track, left_offset):
    verts, codes = [], []

    x, y, heading = (0, 0, 0)
    verts.append((x, y, heading))
    codes.append(Path.MOVETO)
    for segment in track.segments:
        if segment.arc is not None:
            if segment.arc > 0:
                radius = segment.radius - left_offset
            else:
                radius = segment.radius + left_offset

            scale = abs(segment.arc) * radius * KAPPA * 2.0 / pi
            verts.append((x + scale * cos(heading), 
                          y + scale * sin(heading),
                          heading))
            codes.append(Path.CURVE4)

        x, y, heading = segment.step((x, y, heading))

        if segment.arc is None:
            codes.append(Path.LINETO)
        else:
            codes.append(Path.CURVE4)
            verts.append((x - scale * cos(heading), 
                          y - scale * sin(heading),
                          heading))
            codes.append(Path.CURVE4)
        verts.append((x, y, heading))

    vertsL = [(x + left_offset*cos(a + pi/2.0), y + left_offset*sin(a + pi/2.0))
              for (x, y, a) in verts]
    return Path(vertsL, codes)


def draw(track):
    pathL = track_border(track, track.width/2.0)
    pathR = track_border(track, -track.width/2.0)

    fig = plt.figure()
    ax = fig.add_subplot(111, aspect='equal')
    patch = patches.PathPatch(pathL, facecolor='white')
    ax.add_patch(patch)

    patch = patches.PathPatch(pathR, facecolor='none')
    ax.add_patch(patch)

    margin = 100  # in meters
    bbox = pathL.get_extents()
    bbox.update_from_data_xy(pathR.get_extents().get_points(), ignore=False)
    (xmin, ymin), (xmax, ymax) = bbox.get_points()
    ax.set_xlim(xmin - margin, xmax + margin)
    ax.set_ylim(ymin - margin, ymax + margin)
    return fig


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)

    filename = sys.argv[1]
    track = Track.from_xml_file(filename)
    fig = draw(track)

    for filename in sys.argv[2:]:
        x, y = [], []
        for sensors in sensors_gen(filename):
            x.append(sensors.pos3d[0])
            y.append(sensors.pos3d[1])
        plt.plot(x, y, '--')
    plt.show()

# vim: expandtab sw=4 ts=4
