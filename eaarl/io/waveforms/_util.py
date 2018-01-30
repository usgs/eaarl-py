# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
'''Internal utility code for waveforms I/O'''

# Boilerplate for cross-compatibility of Python 2/3
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future.builtins import * # pylint: disable=wildcard-import
import future.standard_library
future.standard_library.install_aliases()

import math
import numpy as np

TIME_FRACTION_SECONDS = 1.6e-6
SCAN_ANGLE_DEGREES = 0.045

def _floor(val):
    '''Returns the floor of its argument, as an integer'''
    try:
        floored = int(math.floor(val))
    except TypeError:
        floored = np.floor(val.astype(np.double)).astype(int)
    return floored

def _round(val):
    '''Rounds its argument to the nearest integer'''
    try:
        rounded = int(val + 0.5)
    except TypeError:
        rounded = np.rint(val.astype(np.double)).astype(int)
    return rounded

def time_int_to_soe(seconds, fraction):
    '''Converts integer time values into floating point seconds

    EAARL stores time values as integer seconds plus an integer fractional
    value. This function converts pairs of such values into floating-point
    seconds of the epoch values.
    '''
    return seconds + TIME_FRACTION_SECONDS * fraction

def time_soe_to_int(soe):
    ''' Converts floating point seconds into integer time values

    EAARL stores time values as integer seconds plus an integer fractional
    value. This function converts floating-point seconds of the epoch values
    into pairs of (integer seconds, fractional seconds).
    '''
    seconds = _floor(soe)
    fraction = _round((soe - seconds) / TIME_FRACTION_SECONDS)
    return (seconds, fraction)

def scan_counts_to_degrees(counts):
    '''Converts scan angle counts values into degrees

    EAARL stores the scan angle as integer counts, due to the mechanism of the
    scan angle digitizer. This function converts counts values into floating
    point degrees.
    '''
    return counts * SCAN_ANGLE_DEGREES

def scan_degrees_to_counts(degrees):
    '''Converts scan angle degrees values into counts

    EAARL stores the scan angle as integer counts, due to the mechanism of the
    scan angle digitizer. This function converts floating point degree values
    into integer counts.
    '''
    return _round(degrees / SCAN_ANGLE_DEGREES)
