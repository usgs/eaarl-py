# pylint: disable=missing-docstring,bad-whitespace

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library # pylint: disable=unused-import
from future.builtins import *

import pytest

from eaarl import analyze

@pytest.mark.parametrize("wf,cent", [
    ([0,1,2,3,4,5,6,7,8,9,10], 7),
    ([0,0,2,8,2,0], 3),
    ([0,10,11,10,11,10,12,14,18,20,15,12,10], 6.875817),
    ([2,4,6], 5./3.),
    ([1,1,1,1,1,1,1], -1),
    ([-1,1,-1,1], 2),
])
def test_centroid(wf, cent):
    assert abs(analyze.centroid(wf) - cent) < 0.00001
