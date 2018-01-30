# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
'''Handling for mission data

.. data:: flip_waveforms

    Specifies whether waveforms should be "flipped" when loading. EAARL
    waveforms are inverted by default. When this setting is True (the default),
    the waveforms are flipped so that they look as one would normally expect.
    Set to False to disable that behavior. Note that other code (such as in
    eaarl.analyze) expects the waveforms to be flipped (so they are not
    inverted), so setting this to False may cause some functions to not yield
    sensible results.
'''

# Boilerplate for cross-compatibility of Python 2/3
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future.builtins import * # pylint: disable=wildcard-import
import future.standard_library
future.standard_library.install_aliases()

import datetime
import json
import os.path

import pandas as pd

from . import gps
from . import ins
from . import waveforms

from ..util import time

# Should waveforms get flipped?
flip_waveforms = True # pylint: disable=invalid-name

class Error(Exception):
    '''Base class for exceptions in this module'''
    pass

class NotLoadedError(Error):
    '''Base for exceptions relating to dependency data not loaded'''
    pass

class OpsNotLoadedError(Error):
    '''Exception raised when ops data is needed but is not loaded'''
    pass

class InsNotLoadedError(Error):
    '''Exception raised when ins data is needed but is not loaded'''
    pass

class GpsNotLoadedError(Error):
    '''Exception raised when gps data is needed but is not loaded'''
    pass

class EdbNotLoadedError(Error):
    '''Exception raised when edb data is needed but is not loaded'''
    pass

class InvalidDateError(Error):
    '''Exception raised when the date doesn't work correctly'''
    def __init__(self, err, message):
        super().__init__(message)
        self.err = err

def create_flight(date, basedir=None, ops=None, ins=None, gps=None, edb=None, zone=None):
    '''Loads a flight with the given configuration

    Parameters
        date : string
            The date of the flight
        basedir : string or None
            If provided, then paths are resolved as relative to this path.
        ops : string or None
            Path to the ops configuration file
        ins : string or None
            Path to the ins file
        gps : string or None
            Path to the gps file
        edb : string or None
            Path to the edb file
        zone : string or None
            UTM zone for the data
    '''
    conf = {'date': date}
    if ops:
        conf['ops'] = ops
    if ins:
        conf['ins'] = ins
    if gps:
        conf['gps'] = gps
    if edb:
        conf['edb'] = edb
    if zone:
        conf['zone'] = zone
    return fromdict(conf, basedir=basedir)

def fromdict(conf, basedir=None):
    '''Loads a flight based on a configuration dict

    Parameters
        basedir : string or None
            If provided, then paths in the configuration will be resolved as
            relative to this path.
    '''
    if basedir is not None:
        # force a copy to avoid modifying original
        conf = dict(conf)
        for field in ['ops', 'ins', 'gps', 'edb']:
            if field in conf:
                conf[field] = os.path.join(basedir, conf[field])

    zone = None
    if 'zone' in conf:
        zone = conf['zone']

    flight = Flight(conf['date'], zone)
    if 'ops' in conf:
        flight.load_ops(conf['ops'])
    if 'ins' in conf:
        flight.load_ins(conf['ins'])
    if 'gps' in conf:
        flight.load_gps(conf['gps'])
    if 'edb' in conf:
        flight.load_edb(conf['edb'])
    return flight

def load(conf_file):
    '''Loads a flight based on a configuration file'''
    with open(conf_file, 'r') as f:
        conf = json.load(f)
    base = os.path.dirname(conf_file)
    return fromdict(conf, base)

class Flight:
    '''Represents a set of raw data sources for an EAARL flight

    This facilitates correlating the data sources together.
    '''

    # pylint: disable=too-many-instance-attributes

    def __init__(self, date, zone=None):
        try:
            self.date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        except TypeError:
            self.date = date

        self.zone = zone

        self.ops_file = None
        self.ops = None
        self.ins_file = None
        self.ins = None
        self.gps_file = None
        self.gps = None
        self.edb_file = None
        self.edb = None

    def gps_time_offset(self):
        '''Returns the time offset between GPS and UTC time for the flight'''
        try:
            return time.gps_utc_offset(self.date)
        except Exception as err:
            raise InvalidDateError(err, 'date is not compatible with datetime.date')

    def soe_day_start(self):
        '''Returns the epoch time for the start of the day of the flight'''
        try:
            return time.date_epoch_seconds(self.date)
        except Exception as err:
            raise InvalidDateError(err, 'date is not compatible with datetime.date')

    def load_ops(self, ops_file):
        '''Loads the given OPS file'''
        self.ops_file = ops_file
        self.ops = json.load(open(ops_file))

    def load_ins(self, ins_file):
        '''Loads the given INS file'''
        if self.ops is None:
            raise OpsNotLoadedError('load_ins requires ops data')
        self.ins_file = ins_file
        self.ins = ins.apply_corrections(ins.read(ins_file),
                                         self.gps_time_offset())

    def load_gps(self, gps_file):
        '''Loads the given GPS file'''
        self.gps_file = gps_file
        self.gps = gps.apply_corrections(gps.read(gps_file),
                                         self.gps_time_offset())

    def load_edb(self, edb_file):
        '''Loads the given EDB file'''
        self.edb_file = edb_file
        self.edb = waveforms.EaarlCollection(edb_file=edb_file)

    def _wfs_extra(self, rasters):
        '''Handles the extra stuff for waveform retrieval

        Performs follow-up handling after raster retrieval:
            * Performs transmit waveform cleaning if ops['tx_clean'] is set.
            * Flattens rasters into pulses, then into waveforms.
            * Interpolates INS data for the waveform records

        Returns pandas.DataFrame of waveform records.
        '''
        if self.ops is None:
            raise OpsNotLoadedError('loading pulses requires ops data')
        if self.ins is None:
            raise InsNotLoadedError('loading pulses requires ins data')

        if 'tx_clean' in self.ops and self.ops['tx_clean'] > 0:
            waveforms.rasters_tx_clean(rasters, self.ops['tx_clean'])
        if flip_waveforms:
            waveforms.rasters_wf_flip(rasters)

        pulses = pd.DataFrame(waveforms.rasters_to_pulses(rasters))
        pulse_sod = pulses['time'] - self.soe_day_start()

        ins.add_to_frame(pulses, pulse_sod, self.ins, self.ops, zone=self.zone)

        pulse_records = pulses.to_dict('records')
        channel_records = waveforms.pulses_to_waveforms(pulse_records)
        wfs = pd.DataFrame(channel_records)

        wfs.set_index(['raster_number', 'pulse_number', 'channel'],
                      drop=False, inplace=True)

        return wfs

    def wfs_by_raster(self, rasters=None, start=None, count=1, ranges=None, progress=True):
        '''Retrieves waveform data for raster numbers

        Returns DataFrame of waveform data for the given raster number(s). If
        start and count are provided, then rasters are returned for the given
        range. If ranges is is provided, then it is treated as a sequence of
        (start, count) entries. If rasters is provided, it should be a sequence
        of raster numbers.

        Parameters
            rasters : int or sequence of ints or None
                Sequence of raster numbers
            start : integer or None
                Starting raster number
            count : integer
                Number of rasters to retrieve
            ranges : sequence of tuples
                Sequence of (start, count) tuples.
            progress : tqdm.tqdm or boolean, default True
                If True and if tqdm is available for import, then a progressbar
                will be displayed during raster reading. Specify False to
                disable. You can also specify your own instance of tqdm.tqdm
                (or compatible) for customizing output.
        '''
        if self.edb is None:
            raise EdbNotLoadedError('loading pulses requires edb data')

        rasts = self.edb.get_rasters(rasters=rasters, start=start, count=count,
                                     ranges=ranges, progress=progress)
        return self._wfs_extra(rasts)

    def wfs_by_time(self, start=None, stop=None, ranges=None, progress=True):
        '''Retrieve waveform data for given time ranges

        Returns DataFrame of waveform data for the given time range(s). If
        start and stop are provided, then data for rasters are returned such
        that start <= raster start time < stop. If ranges is provided, then
        each tuple of start, stop are used.

        Parameters
            start : numeric or None
                A start time
            stop : numeric or None
                A stop time
            ranges : sequence or None
                Sequence of start and stop tuples.
            progress : tqdm.tqdm or boolean, default True
                If True and if tqdm is available for import, then a progressbar
                will be displayed during raster reading. Specify False to
                disable. You can also specify your own instance of tqdm.tqdm
                (or compatible) for customizing output.
        '''
        if self.edb is None:
            raise EdbNotLoadedError('loading pulses requires edb data')

        rasters = self.edb.get_rasters_by_time(start=start, stop=stop,
                                               ranges=ranges, progress=progress)
        return self._wfs_extra(rasters)

    def times_by_region(self, region):
        '''Retrieve time ranges corresponding to a region

        This determines the time periods where the plane was within the bounds
        of the given region.

        Parameters
            region : shapely.geometry.base.BaseGeometry
                Region of interest to retrieve time ranges for, using WGS-84
                geographic coordinates
        '''
        import shapely.geometry

        if self.gps is not None:
            lon, lat = self.gps.lon, self.gps.lat
            soe = self.gps.sod + self.soe_day_start()
        elif self.ins is not None:
            lon, lat = self.ins.lon, self.ins.lat
            soe = self.ins.sod + self.soe_day_start()
        else:
            raise GpsNotLoadedError('time determination requires gps or ins data')

        ranges = []
        last = None
        for i, x, y, t in zip(range(len(lon)), lon, lat, soe):
            point = shapely.geometry.Point(x, y)
            if region.contains(point):
                if last is None:
                    ranges = [[t, t]]
                elif i == last + 1:
                    ranges[-1][1] = t
                else:
                    ranges.append([t, t])
                last = i

        return ranges

    def wfs_by_region(self, region, progress=True):
        '''Retrieve waveform data corresponding to a region

        This retrieves data for records where the plane was within the given
        region. In other words, the data is retrieved based on the plane's
        location instead of the target locations. You may need to expand your
        region by a few hundred meters to compensate.

        Parameters
            region : shapely.geometry.base.BaseGeometry
                Region of interest to retrieve pulse data for, using WGS-84
                geographic coordinates
            progress : tqdm.tqdm or boolean, default True
                If True and if tqdm is available for import, then a progressbar
                will be displayed during raster reading. Specify False to
                disable. You can also specify your own instance of tqdm.tqdm
                (or compatible) for customizing output.
        '''
        ranges = self.times_by_region(region)
        return self.wfs_by_time(ranges=ranges, progress=progress)

    def asdict(self, basedir=None):
        '''Returns the configuration for the flight as a dict

        Parameters
            basedir : string or None
                If provided, the paths for files will be relative to this
                directory.
        '''
        conf = {}
        conf['date'] = self.date.isoformat()
        if self.zone is not None:
            conf['zone'] = self.zone
        for field in ['ops', 'ins', 'gps', 'edb']:
            if self.__dict__[field + '_file'] is not None:
                value = self.__dict__[field + '_file']
                if basedir is not None:
                    value = os.path.relpath(value, basedir)
                conf[field] = value
        return conf

    def save(self, conf_file):
        '''Saves the configuration for the flight to a file'''
        conf = self.asdict()
        base = os.path.dirname(conf_file)
        conf = self.asdict(base)
        with open(conf_file, 'w') as f:
            json.dump(conf, f, sort_keys=True, indent=4)
