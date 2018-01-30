# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
'''Conversion to/from UTM'''

# Boilerplate for cross-compatibility of Python 2/3
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future.builtins import * # pylint: disable=wildcard-import
import future.standard_library
future.standard_library.install_aliases()

import datetime

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
    '''Returns the offset in seconds between UTC and GPS time on a date'''
    leap = [d for d in LEAP_DATES if d < date]
    return len(leap)
