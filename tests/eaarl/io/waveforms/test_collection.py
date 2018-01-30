from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
from future.builtins import *

import bz2
import datetime
import gzip
import numpy as np
import os
import os.path
import pandas as pd
import shutil
import tempfile
import unittest

from eaarl.io.waveforms import collection
from eaarl.io.waveforms import tld

class TestEaarlCollection(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

        epoch = datetime.datetime(1970, 1, 1)
        start = (datetime.datetime(2016, 1, 1, 10) - epoch).total_seconds()
        stop = (datetime.datetime(2016, 1, 1, 11) - epoch).total_seconds()
        times = np.linspace(start, stop, 30)
        self.times = times

        file_names = pd.to_datetime(
            (
                times[0::5].astype('datetime64[s]')[np.newaxis,].T +
                np.zeros(5, dtype='timedelta64[s]')
            ).flatten()
        ).strftime('%y%m%d-%H%M%S.tld')

        edb = []

        for start in range(0, 30, 5):
            fn = os.path.join(self.dir, file_names[start])
            fh = open(fn, 'wb+')
            for idx in range(start, start+5):
                edb.append({
                    'record_offset': fh.tell(),
                    'record_length': 0,
                    'file_name': file_names[idx],
                    'pulse_count': 0,
                    'digitizer': 0,
                    'time': times[idx],
                })
                tld.write(fh, [{
                    'time': times[idx],
                    'raster_number': idx+1,
                    'digitizer': 0,
                    'pulse': [],
                }])
            fh.close()

        self.eaarl = collection.EaarlCollection(edb_data=edb, tld_path=self.dir)

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_get_rasters_single(self):
        raster = self.eaarl.get_rasters(2)
        self.assertEqual(len(raster), 1)
        self.assertEqual(raster[0]['raster_number'], 2)

    def test_get_rasters_list(self):
        raster = self.eaarl.get_rasters([2,3])
        self.assertEqual(len(raster), 2)
        self.assertEqual(raster[0]['raster_number'], 2)
        self.assertEqual(raster[1]['raster_number'], 3)

    def test_get_rasters_list_gap(self):
        raster = self.eaarl.get_rasters([2,4])
        self.assertEqual(len(raster), 2)
        self.assertEqual(raster[0]['raster_number'], 2)
        self.assertEqual(raster[1]['raster_number'], 4)

    def test_get_rasters_list_multifile(self):
        raster = self.eaarl.get_rasters([2,8])
        self.assertEqual(len(raster), 2)
        self.assertEqual(raster[0]['raster_number'], 2)
        self.assertEqual(raster[1]['raster_number'], 8)

    def test_get_rasters_list_sorts(self):
        raster = self.eaarl.get_rasters([4,2])
        self.assertEqual(len(raster), 2)
        self.assertEqual(raster[0]['raster_number'], 2)
        self.assertEqual(raster[1]['raster_number'], 4)

    def test_get_rasters_start(self):
        raster = self.eaarl.get_rasters(start=2)
        self.assertEqual(len(raster), 1)
        self.assertEqual(raster[0]['raster_number'], 2)

    def test_get_rasters_start_count(self):
        raster = self.eaarl.get_rasters(start=2, count=2)
        self.assertEqual(len(raster), 2)
        self.assertEqual(raster[0]['raster_number'], 2)
        self.assertEqual(raster[1]['raster_number'], 3)

    def test_get_rasters_ranges(self):
        raster = self.eaarl.get_rasters(ranges=[(1,2),(7,8)])
        self.assertEqual(len(raster), 10)
        expected = list(range(1,3)) + list(range(7,15))
        for idx, rn in zip(range(10), expected):
            self.assertEqual(raster[idx]['raster_number'], rn)

    def test_lookup_time_start_stop(self):
        start = self.times[2] - 0.001
        stop = self.times[4] + 0.001
        rns = self.eaarl.lookup_rasters_by_time(start, stop)
        self.assertEqual(list(rns), [3,4,5])

    def test_lookup_time_ranges(self):
        ranges = [
            (self.times[2] - 0.001, self.times[4] + 0.001),
            (self.times[6] - 0.001, self.times[9] + 0.001),
        ]
        expected = [3,4,5,7,8,9,10]
        rns = self.eaarl.lookup_rasters_by_time(ranges=ranges)
        self.assertEqual(list(rns), expected)

    def test_get_by_time(self):
        start = self.times[2] - 0.001
        stop = self.times[4] + 0.001
        raster = self.eaarl.get_rasters_by_time(start, stop)
        self.assertEqual(len(raster), 3)
        self.assertEqual(raster[0]['raster_number'], 3)
        self.assertEqual(raster[1]['raster_number'], 4)
        self.assertEqual(raster[2]['raster_number'], 5)

class TestOpenTldFile(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.file = 'file.tld'
        self.data = (
            b'\x45\x41\x41\x52\x4c\x20\x69\x73'
            b'\x20\x61\x77\x65\x73\x6f\x6d\x65'
        )

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_plain(self):
        fn = os.path.join(self.dir, self.file)
        with open(fn, 'wb') as fh:
            fh.write(self.data)
        data = None
        with collection._open_tld_file(self.dir, self.file) as fh:
            data = fh.read()
        self.assertEqual(data, self.data)

    def test_gz(self):
        fn = os.path.join(self.dir, self.file + '.gz')
        with gzip.open(fn, 'wb') as fh:
            fh.write(self.data)
        data = None
        with collection._open_tld_file(self.dir, self.file) as fh:
            data = fh.read()
        self.assertEqual(data, self.data)

    def test_bz(self):
        fn = os.path.join(self.dir, self.file + '.bz2')
        with bz2.BZ2File(fn, 'wb') as fh:
            fh.write(self.data)
        data = None
        with collection._open_tld_file(self.dir, self.file) as fh:
            data = fh.read()
        self.assertEqual(data, self.data)

    def test_sub_plain(self):
        os.mkdir(os.path.join(self.dir, 'eaarl'))
        fn = os.path.join(self.dir, 'eaarl', self.file)
        with open(fn, 'wb') as fh:
            fh.write(self.data)
        data = None
        with collection._open_tld_file(self.dir, self.file) as fh:
            data = fh.read()
        self.assertEqual(data, self.data)

    def test_sub_gz(self):
        os.mkdir(os.path.join(self.dir, 'eaarl'))
        fn = os.path.join(self.dir, 'eaarl', self.file + '.gz')
        with gzip.open(fn, 'wb') as fh:
            fh.write(self.data)
        data = None
        with collection._open_tld_file(self.dir, self.file) as fh:
            data = fh.read()
        self.assertEqual(data, self.data)

    def test_sub_bz(self):
        os.mkdir(os.path.join(self.dir, 'eaarl'))
        fn = os.path.join(self.dir, 'eaarl', self.file + '.bz2')
        with bz2.BZ2File(fn, 'wb') as fh:
            fh.write(self.data)
        data = None
        with collection._open_tld_file(self.dir, self.file) as fh:
            data = fh.read()
        self.assertEqual(data, self.data)
