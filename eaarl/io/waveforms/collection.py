# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
'''Handling for a collection of TLD waveform data'''

# Boilerplate for cross-compatibility of Python 2/3
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future.builtins import * # pylint: disable=wildcard-import
import future.standard_library
future.standard_library.install_aliases()

from contextlib import contextmanager as _contextmanager
import bz2
import gzip
import numpy as np
import os.path
import pandas as pd

from . import edb
from . import tld

@_contextmanager
def collection_open(*args, **kwds):
    '''Context manager for an :class:`EaarlCollection`.'''
    yield EaarlCollection(*args, **kwds)

class EaarlCollection:
    '''Collection of EAARL waveform data.

    The collection comprises an EDB file and associated TLD files.
    '''
    def __init__(self, edb_file=None, tld_path=None, edb_data=None):
        '''Create an EaarlCollection

        Parameters
            edb_file : string or None
                Path to an EDB file
            tld_path : string or None
                Path to the TLD files
            edb_data : sequence of dicts or None
                Return result from :func:`eaarl.io.waveforms.edb.read`.
        '''
        if tld_path is not None:
            self._tld_path = tld_path
        elif edb_file is not None:
            self._tld_path = os.path.dirname(edb_file)
        else:
            raise TypeError(
                'EaarlCollection must be initialized with either tld_path= or '
                'edb_file='
            )

        if edb_data is not None:
            self._edb = pd.DataFrame(edb_data).copy(deep=True)
        else:
            try:
                raw_edb = edb.read_from(edb_file)
            except TypeError:
                raw_edb = edb.read(edb_file)
            self._edb = pd.DataFrame(raw_edb)

        self._edb['raster_number'] = range(1, len(self._edb)+1)

    def get_rasters_by_time(self, start=None, stop=None, ranges=None, progress=True):
        '''Retrieve raster data for given time ranges

        Returns array of dicts containing the raster data. If start and stop
        are provided, then records are returned such that start <= raster time
        < stop. If ranges is provided, then each tuple of start, stop are used.

        Parameters
            start : numeric or None
                A start time
            stop : numeric or None
                A stop time
            ranges : sequence of tuples or None
                Sequence of *(start, stop)* tuples
            progress : tqdm.tqdm or boolean, default True
                If True and if tqdm is available for import, then a progressbar
                will be displayed during raster reading. Specify False to
                disable. You can also specify your own instance of tqdm.tqdm
                (or compatible) for customizing output.
        '''
        rasters = self.lookup_rasters_by_time(start, stop, ranges)
        return self.get_rasters(rasters, progress=progress)

    def lookup_rasters_by_time(self, start=None, stop=None, ranges=None):
        '''Lookup raster number for given times

        Returns array of raster numbers. If start and stop are provided, then
        record numbers are returned such that start <= raster time < stop. If
        ranges is provided, then each tuple of start, stop are used.

        Parameters
            start : numeric or None
                A start time
            stop : numeric or None
                A stop time
            ranges : sequence of tuples or None
                Sequence of start and stop tuples
        '''
        if start is not None and stop is not None:
            time_ranges = [(start, stop)]
        elif ranges is not None:
            time_ranges = ranges
        else:
            raise TypeError(
                'lookup_rasters_by_time() requires ranges= or start= and stop='
            )

        match = np.zeros(len(self._edb), dtype=bool)
        time = self._edb['time']
        for time_start, time_stop in time_ranges:
            match |= ((time >= time_start) & (time <= time_stop))

        return self._edb[match]['raster_number'].as_matrix()

    def get_rasters(self, rasters=None, start=None, count=1, ranges=None, progress=True):
        '''Retrieve raster data for raster numbers

        Returns array of dicts containing the raster data. If start and count
        are provided, then raster records are provided for the given range. If
        ranges is provided, then it is treated as a sequence of (start, count)
        entries. If rasters is provided, it should be a sequence of raster
        numbers.

        Parameters
            rasters : integer or sequence of integers or None
                Mission data for a flight
            start : integer or None
                Starting raster number
            count : integer, default 1
                Number of rasters to retrieve
            ranges : sequence of tuples
                Sequence of (start, count) tuples.
            progress : tqdm.tqdm or boolean, default True
                If True and if tqdm is available for import, then a progressbar
                will be displayed during raster reading. Specify False to
                disable. You can also specify your own instance of tqdm.tqdm
                (or compatible) for customizing output.
        '''
        # pylint: disable=too-many-locals,too-many-branches

        want = np.zeros(len(self._edb), dtype='bool')

        if rasters is not None:
            rasters = np.array(rasters, dtype='int')
            want[rasters-1] = True

        if start is not None:
            want[start-1:start+count-1] = True

        if ranges is not None:
            for _start, _count in ranges:
                want[_start-1:_start+_count-1] = True

        _edb = self._edb[want]
        if _edb.empty:
            return []
        _edb = _edb.reset_index(drop=True)

        _edb['rank'] = (_edb['raster_number'].diff()-1).cumsum()
        _edb['rank'].iat[0] = 0
        _edb['rank'] = _edb['rank'].astype('int')

        bar = False
        if progress is True:
            try:
                from tqdm import tqdm
            except ImportError:
                pass
            else:
                bar = tqdm(desc='Loading rasters', unit='raster',
                           smoothing=0.1, total=len(_edb), ncols=72)
        elif progress:
            bar = progress

        records = []
        for file_name, edb_by_file in _edb.groupby('file_name'):
            with _open_tld_file(self._tld_path, file_name) as f:
                for _, edb_run in edb_by_file.groupby('rank'):
                    offset = edb_run['record_offset'].iat[0]
                    records.extend(tld.read(f, offset, len(edb_run), progress=bar))

        if progress is True and bar:
            bar.close()

        # Replace cyclic raster_number from file with raster_number defined by
        # the EDB file
        for raster, record in zip(_edb.raster_number, records):
            record['raster_number'] = raster

        return records

@_contextmanager
def _open_tld_file(path, tld_file):
    '''Helper context manager wrapper for TLD files

    Opens the given file, handling compression as needed. Also handles
    detection of whether the file is in an eaarl subdirectory.

    Parameters
        path : string
            Path where the TLD file is expected to be found.
        tld_file : string
            Name of the file to open.
    '''
    # Select file with least amount of compression, which may result in faster
    # reads. If can't find any in same directory as EDB file, then check for an
    # eaarl subdirectory as some datasets were organized that way.
    candidates = [
        os.path.join(path, tld_file),
        os.path.join(path, tld_file + '.gz'),
        os.path.join(path, tld_file + '.bz2'),
        os.path.join(path, 'eaarl', tld_file),
        os.path.join(path, 'eaarl', tld_file + '.gz'),
        os.path.join(path, 'eaarl', tld_file + '.bz2'),
    ]

    tld_path = None
    for tld_path in candidates:
        if os.path.isfile(tld_path):
            break
    else:
        raise FileNotFoundError('Unable to find ' + tld_file)

    if tld_path[-4:] == '.bz2':
        open_fnc = bz2.BZ2File
    elif tld_path[-3:] == '.gz':
        open_fnc = gzip.open
    else:
        open_fnc = open
    with open_fnc(tld_path, 'rb') as f:
        yield f

def rasters_to_pulses(rasters):
    '''Flatten sequence of rasters to sequence of pulses

    Raster records contain a pulse entry that is a list of pulse records. This
    flattens it to combine raster and pulse data for each pulse.

    Parameters
        rasters : sequence of dicts
            Raster data

    Returns sequence of dicts
    '''
    pulses = []
    for raster in rasters:
        for pulse_number in range(1, raster['pulse_count']+1):
            pulse = raster.copy()
            del pulse['pulse']
            del pulse['time']
            pulse.update(raster['pulse'][pulse_number-1])
            pulse['pulse_number'] = pulse_number
            pulses.append(pulse)
    return pulses

def pulses_to_waveforms(pulses):
    '''Flatten sequence of pulses for their waveforms

    The channel related fields are flattened out for each channel, with each
    pulse duplicated for each of the channels.

    Parameters
        pulses : sequence of dicts
            Pulse data

    Returns sequence of dicts
    '''
    def flatten_channel(pulse, idx):
        '''Flatten a pulse for each channel'''
        for field in ['bias_rx', 'rx']:
            if field in pulse:
                pulse[field] = pulse[field][idx]

    wfs = []
    for pulse in pulses:
        for channel in range(1, len(pulse['rx'])+1):
            wf = pulse.copy()
            wf['channel'] = channel
            try:
                flatten_channel(wf, channel-1)
            except IndexError:
                pass
            else:
                wfs.append(wf)
    return wfs

def rasters_tx_clean(rasters, pos):
    '''Cleans up the transmit waveforms

    Sets all sample values in the tx waveforms starting at 1-based index pos to
    the same as the first sample value in the waveform.

    Parameters
        rasters : sequence of dicts
            Sequence of dicts that contain pulse entries, which in turn contain
            tx entries
        pos : integer
            1-based index into the transmit waveforms where cleaning should
            start
    '''
    for raster in rasters:
        for pulse in raster['pulse']:
            pulse['tx'] = np.array(pulse['tx'])
            pulse['tx'][pos-1:] = pulse['tx'][0]

def rasters_wf_flip(rasters):
    '''Flips the tx and rx waveforms

    EAARL raw waveforms are inverted: high sample values indicate a low
    response and low sample values indicate a high response. This function
    flips the values so that low responses have low values and high responses
    have high values.

    Parameters
        rasters : sequence of dicts
            Sequence of dicts that contain pulse entries, which in turn contain
            tx and rx entries
    '''
    for raster in rasters:
        for pulse in raster['pulse']:
            pulse['tx'] = 255 - np.array(pulse['tx'])
            pulse['rx'] = [255 - np.array(x) for x in pulse['rx']]
