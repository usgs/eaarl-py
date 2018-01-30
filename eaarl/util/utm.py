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

import numpy as np
import utm

_from_latlon = np.frompyfunc(utm.from_latlon, 3, 4) # pylint: disable=invalid-name
def from_latlon(latitude, longitude, force_zone_number=None):
    '''Converts geographic coordinates to UTM coordinates

    Parameters
        latitude : array-like of float
            Latitude coordinate values
        longitude : array-like of float
            Longitude coordinate values
        force_zone_number : integer or None
            Forces the coordinates to the given UTM zone. If omitted, then points
            are converted to their native UTM zones.

    Returns : (array, array, array, array)
        Returns (easting, northing, zone_number, zone_letter) where each are
        arrays.
    '''
    return _from_latlon(latitude, longitude, force_zone_number)

_to_latlon = np.frompyfunc(utm.to_latlon, 5, 2) # pylint: disable=invalid-name
def to_latlon(easting, northing, zone_number, zone_letter=None, northern=None):
    '''Converts UTM coordinates to geographic coordinates

    Parameters
        easting : array-like of floats
            Easting of the coordinates.
        northing : array-like of floats
            Northern of the coordinates.
        zone_number : integer or array-like of integers
            Zone of the coordinates.
        zone_letter : string or array-like of string or None
            Specifies the zone letters. This is used to determine whether the
            coordinates are in the northern or southern hemisphere. If omitted,
            then northern is used.
        northern : Boolean or array-like of Booleans or None
            Indicates whether coordinates are in the southern (False) or northern
            (True) hemisphere. Default is None, which is treated as True. Ignored
            if zone_letter specified.

    Returns : (array, array)
        Returns (latitude, longitude) where each are arrays.
    '''
    if not zone_letter and northern is None:
        northern = True
    return _to_latlon(easting, northing, zone_number, zone_letter, northern)
