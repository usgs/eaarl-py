# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
'''Process raw data to derive pointeger records
'''

# Boilerplate for cross-compatibility of Python 2/3
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future.builtins import * # pylint: disable=wildcard-import
import future.standard_library
future.standard_library.install_aliases()

import numpy as np

import eaarl.io.waveforms
import eaarl.project
import eaarl.util.utm

def remove_failed_thresh(frame, rx=True, tx=True):
    '''Removes records with failed rx/tx thresholds.

    Parameters
        frame : pandas.DataFrame
            DataFrame to discard records from. Must contain fields thresh_rx
            and thresh_tx.
        rx : bool
            If True, discard records where thersh_rx == 1.
        tx : bool
            If True, discard records where thersh_tx == 1.

    Returns : pandas.DataFrame
        New pandas.DataFrame with kept records.
    '''
    if rx:
        frame = frame[frame.thresh_rx == 0]
    if tx:
        frame = frame[frame.thresh_tx == 0]
    return frame

def add_mirror(frame, ops):
    '''Adds the mirror location to the records

    Adds four fields to the dataframe: tx_pos, which is the centroid of the
    waveform; and mir_x, mir_y, and mir_z, which are the UTM coordinates of the
    mirror on the plane.

    Parameters
        frame : pandas.DataFrame
            Dataframe with waveform records.

    '''
    frame['tx_pos'] = centroid_array(frame.tx, None)
    eaarl.project.project_mirror(frame, ops)
    return frame

def add_fs(frame, ops, prefix='fs', limit=12):
    r'''Add the first surface target to the waveform data using centroid

    Detects a target using the centroid of the waveform. This will generally
    correspond to the first surface.

    Adds five fields to the dataframe: fs_pos, which is the position in the
    waveform of the target; fs_range, which is the distance in meters between
    the mirror and the target; and fx_x, fs_y, and fs_z, which are the UTM
    coordinates of the target.

    Parameters
        frame : pandas.DataFrame
            DataFrame with pulse data as returned by :func:`get_for_region`,
            :func:`get_by_time`, or :func:`get_by_rasters`.
        ops : dict
            The ops data, available as flight.ops on an eaarl.io.flight.Flight
            or by manually loading an ops file as a dict.
        prefix : string, default "fs\_"
            Allows you to change the prefix for the fields added to the
            dataframe.
        limit : integer or None, default 12
            Limits how many samples of the waveform are used for the centroid
            calculation. By default, the first 12 samples are used.
    '''
    frame[prefix + '_pos'] = centroid_array(frame.rx, limit)
    frame[prefix + '_range'] = eaarl.project.target_range(
        frame['range'], frame['tx_pos'], frame[prefix + '_pos'],
        frame['channel'], ops)
    eaarl.project.project_point(frame, ops, frame[prefix + '_range'], prefix)
    return frame

def centroid(wf, limit=None):
    '''Returns the centroid of the waveform

    Returns the 0-based index into the waveform where the centroid is located.
    If a centroid cannot be calculated, returns -1.

    Parameters
        wf : sequence of numbers
            Any sequence of numbers suitable as input to np.array, representing
            the sample values for the digitized waveform.
    '''
    wf = np.array(wf)

    if wf.size == 0:
        return -1

    if limit:
        wf = wf[:limit]

    # Remove background energy
    wf = (wf - wf[0]).astype(float)

    # Avoid divide-by-zero
    sum_power = wf.sum()
    if sum_power == 0:
        return -1

    # Need to index from 1 instead of 0 so that first value has weight
    weighted_idx = wf * np.arange(1, len(wf) + 1)
    weighted_sum = weighted_idx.sum()

    # -1 is necessary to convert from 1-based index to 0-based index
    return weighted_sum / sum_power - 1

# Wrapper around centroid for use on arrays
centroid_array = np.frompyfunc(centroid, 2, 1) # pylint: disable=invalid-name
