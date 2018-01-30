# pylint: disable=missing-docstring,bad-whitespace

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library # pylint: disable=unused-import
from future.builtins import *

import numpy as np
import numpy.testing as nptest

from eaarl import rcf

def test_rcf():
    jury = np.array([100,101,100,99,60,98,99,101,105,103,30,88,99,110,101,150])
    low = rcf.rcf_jury(jury, 6)
    assert low == 98

def test_gridded():
    base = np.broadcast_to(np.arange(0, 20, 2), (10, 10))

    x = base.flatten('C')
    y = base.flatten('F')
    z = np.arange(1, 101)

    actual = rcf.rcf_grid(x, y, z, 5, 10, 2)
    expected = np.broadcast_to(
        np.concatenate((np.zeros(40), np.ones(10)))[np.newaxis,:],
        (2, 50)).flatten('C').astype('bool')

    nptest.assert_equal(actual, expected)
