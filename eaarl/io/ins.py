# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
'''Handling for ins trajectory file'''

# Boilerplate for cross-compatibility of Python 2/3
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future.builtins import * # pylint: disable=wildcard-import
import future.standard_library
future.standard_library.install_aliases()

import numpy as np
import pandas as pd
import tables

from ..util.utm import from_latlon

def read(filename):
    '''Read INS data from a given HDF5 or CSV file

    Returns : pandas.DataFrame
        Returns a DataFrame with the file's data.
    '''
    try:
        with tables.open_file(filename, 'r') as f:
            h5data = f.root.ins.read()
        return pd.DataFrame(h5data)
    except tables.exceptions.HDF5ExtError:
        return pd.read_csv(filename)

def _unwrap(degrees):
    '''Updates angles to avoid big jumps

    For example, [359, 1] becomes [359, 361].'''
    return np.rad2deg(np.unwrap(np.deg2rad(degrees)))

def apply_corrections(ins, gps_time_offset=0):
    '''Update INS data with relevant corrections

    The timestamp in an INS file can originally be in seconds-of-the-week
    format. This converts it to seconds-of-the-mission-day format.

    The heading is also "unwrapped" so the angle values avoid big jumps. For
    example, the sequence [359, 1] will become [359, 361]. This speeds up
    interpolation.

    Parameters
        ins : pandas.DataFrame
            A DataFrame containing the INS data
        gps_time_offset : numeric
            GPS time offset to apply to the data to convert it to UTC time.

    Returns : pandas.DataFrame
        Returns the modified ins DataFrame.
    '''
    day_start = int(ins.sod[0] / 86400) * 86400
    ins['sod'] -= day_start
    ins['sod'] += gps_time_offset

    ins[ins.sod < 0]['sod'] += 604800

    ins['heading'] = _unwrap(ins.heading)

    return ins

def add_to_frame(frame, sod, ins, ops=None, prefix='ins_', zone=None):
    r'''Adds interpolated INS data to a frame

    Adds the following fields to the given dataframe:
        * ins_lon - longitude of GPS antenna in degrees
        * ins_lat - latitude of GPS antenna in degrees
        * ins_alt - altitude of GPS antenna in meters
        * ins_roll - roll of INS in degrees
        * ins_pitch - pitch of INS in degrees
        * ins_heading - heading of INS in degrees
        * ins_east - UTM easting of GPS antenna in meters
        * ins_north - UTM northing of GPS antenna in meters
        * ins_zone - UTM zone for ins_east and ins_north

    Parameters
        frame : pandas.DataFrame
            A pandas DataFrame that will have fields added to it
        sod : np.array or pandas.Series
            Seconds-of-the-day time values that correspond to the records in
            the frame
        ins : pandas.DataFrame
            INS data to interpolate from
        ops : dict
            The ops data for the flight
        prefix : string, default "ins\_"
            Allows you to change the prefix used for the added fields.
        zone : number or None
            Allows you to specify a UTM zone that should be used when deriving
            the northing and easting values

    Returns : pandas.DataFrame
        Returns the DataFrame that was passed to it, which now contains added
        fields.
    '''
    ops = ops or {}

    def _interp(field):
        return np.interp(sod, ins.sod, field, left=np.nan, right=np.nan)

    fields = ['lon', 'lat', 'alt', 'roll', 'pitch', 'heading']
    for field in fields:
        frame[prefix + field] = _interp(ins[field])

    if 'dmars_invert' in ops and ops['dmars_invert']:
        frame[prefix + 'roll'] *= -1
        frame[prefix + 'pitch'] *= -1
        frame[prefix + 'heading'] += 180

    # If any of the requested sod values are outside the bounds of the INS,
    # then the corresponding values will be nan. The UTM conversion in
    # from_latlon fails if any values are nan, so avoid passing them to it.

    valid = ~np.isnan(frame[prefix + 'lon']) & ~np.isnan(frame[prefix + 'lat'])

    frame[prefix + 'east'] = np.nan
    frame[prefix + 'north'] = np.nan
    frame[prefix + 'zone'] = np.nan
    (
        frame.loc[valid, prefix + 'east'], frame.loc[valid, prefix + 'north'],
        frame.loc[valid, prefix + 'zone'], _
    ) = from_latlon(frame[prefix + 'lat'][valid],
                    frame[prefix + 'lon'][valid], zone)

    return frame
