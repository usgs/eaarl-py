# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
'''Time utility functions'''

# Boilerplate for cross-compatibility of Python 2/3
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future.builtins import * # pylint: disable=wildcard-import
import future.standard_library
future.standard_library.install_aliases()

import datetime

# When updating this list, be sure to update the documentation for
# gps_utc_offset.
LEAP_DATES = [
    datetime.date(1981, 6, 30),
    datetime.date(1982, 6, 30),
    datetime.date(1983, 6, 30),
    datetime.date(1985, 6, 30),
    datetime.date(1987, 12, 31),
    datetime.date(1989, 12, 31),
    datetime.date(1990, 12, 31),
    datetime.date(1992, 6, 30),
    datetime.date(1993, 6, 30),
    datetime.date(1994, 6, 30),
    datetime.date(1995, 12, 31),
    datetime.date(1997, 6, 30),
    datetime.date(1998, 12, 31),
    datetime.date(2005, 12, 31),
    datetime.date(2008, 12, 31),
    datetime.date(2012, 6, 30),
    datetime.date(2015, 6, 30),
    datetime.date(2016, 12, 31)
]

def date_epoch_seconds(date):
    '''Returns the seconds-of-the-epoch time for the start of a date'''
    delta = date - datetime.date(1970, 1, 1)
    return delta.total_seconds()

def gps_utc_offset(date):
    '''Returns the offset in seconds between UTC and GPS time on a date

    .. warning::

        The offset is calculated using a hard-coded list of UTC leap second
        dates. If leap seconds are added in the future,
        *eaarl.util.time.LEAP_DATES* will need to be updated. Leap seconds are
        announced by the International Earth Rotation and Reference Systems
        Service (IERS) via Bulletin C. See http://hpiers.obspm.fr/eop-pc for
        more information. The list of leap second dates in *LEAP_DATES* is
        currently accurate through at least June 2018.
    '''
    leap = [d for d in LEAP_DATES if d < date]
    return len(leap)
