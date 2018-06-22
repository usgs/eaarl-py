# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
'''Handling for gps trajectory files'''

# Boilerplate for cross-compatibility of Python 2/3
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future.builtins import * # pylint: disable=wildcard-import
import future.standard_library
future.standard_library.install_aliases()

import pandas as pd
import tables

def read(filename):
    '''Read GPS data from a given HDF5 or CSV file

    Returns : pandas.DataFrame
        Returns a DataFrame with the file's data.
    '''
    try:
        with tables.open_file(filename, 'r') as f:
            h5data = f.root.gps.read()
        return pd.DataFrame(h5data)
    except tables.exceptions.HDF5ExtError:
        return pd.read_csv(filename)

def apply_corrections(gps, gps_time_offset=0):
    '''Applies time correction to gps data

    Parameters
        gps : pandas.DataFrame
            GPS data as returned by :func:`read`.
        gps_time_offset : numeric
            GPS time offset to apply to the data to convert it to UTC time.

    Returns : pandas.DataFrame
        Returns the modified gps DataFrame.
    '''
    gps['sod'] += gps_time_offset
    return gps
