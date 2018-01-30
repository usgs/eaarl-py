from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
from future.builtins import *

import pytest
import datetime

from eaarl.util import time

@pytest.mark.parametrize("year, month, day, seconds", [
    (1970, 1, 1, 0),
    (1970, 1, 2, 86400),
    (1995, 12, 25, 819849600),
    (2014, 2, 14, 1392336000),
])
def test_date_epoch_seconds(year, month, day, seconds):
    date = datetime.date(year, month, day)
    assert time.date_epoch_seconds(date) == seconds

@pytest.mark.parametrize("year, month, day, offset", [
    (1981, 6, 30, 0),
    (1981, 7, 1, 1),
    (1982, 6, 30, 1),
    (1982, 7, 1, 2),
    (1983, 6, 30, 2),
    (1983, 7, 1, 3),
    (1984, 4, 8, 3),
    (1985, 6, 30, 3),
    (1985, 7, 1, 4),
    (1986, 8, 6, 4),
    (1987, 12, 31, 4),
    (1988, 1, 1, 5),
    (1989, 12, 31, 5),
    (1990, 1, 1, 6),
    (1990, 12, 31, 6),
    (1991, 1, 1, 7),
    (1992, 6, 30, 7),
    (1992, 7, 1, 8),
    (1993, 6, 30, 8),
    (1993, 7, 1, 9),
    (1994, 6, 30, 9),
    (1994, 7, 1, 10),
    (1995, 12, 31, 10),
    (1996, 1, 1, 11),
    (1997, 6, 30, 11),
    (1997, 7, 1, 12),
    (1998, 12, 31, 12),
    (1999, 1, 1, 13),
    (2000, 2, 2, 13),
    (2001, 3, 3, 13),
    (2002, 4, 4, 13),
    (2003, 5, 5, 13),
    (2004, 6, 6, 13),
    (2005, 12, 31, 13),
    (2006, 1, 1, 14),
    (2007, 6, 1, 14),
    (2008, 12, 31, 14),
    (2009, 1, 1, 15),
    (2010, 11, 5, 15),
    (2011, 7, 11, 15),
    (2012, 6, 30, 15),
    (2012, 7, 1, 16),
    (2013, 2, 10, 16),
    (2014, 5, 12, 16),
    (2015, 6, 30, 16),
    (2015, 7, 1, 17),
    (2016, 12, 31, 17),
    (2017, 1, 1, 18),
])
def test_gps_utc_offset(year, month, day, offset):
    date = datetime.date(year, month, day)
    assert time.gps_utc_offset(date) == offset

