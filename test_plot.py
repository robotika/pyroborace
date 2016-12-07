import math
import tempfile
import unittest

from plot import draw
from segment import Segment
from track import Track


class PlotTest(unittest.TestCase):

    def test_draw(self):
        line = Segment(length=100.0)
        arc = Segment(arc=math.radians(90), radius=50.0)

        track = Track([line, arc]*4, width = 20)
        fig = draw(track)
        with tempfile.TemporaryFile() as f:
            fig.savefig(f, format='png')

# vim: expandtab sw=4 ts=4
