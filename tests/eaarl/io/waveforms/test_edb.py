from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
from future.builtins import *

import unittest
from io import BytesIO

from eaarl.io.waveforms import edb

class TestEdb(unittest.TestCase):
    def setUp(self):
        self.raw = (
            b'\x48\x00\x00\x00' # files_offset
            b'\x03\x00\x00\x00' # record_count
            b'\x02\x00\x00\x00' # file_count

            # Raster 1
            b'\x01\x00\x00\x00' # time_seconds
            b'\x02\x00\x00\x00' # time_fraction
            b'\x03\x00\x00\x00' # record_offset
            b'\x04\x00\x00\x00' # record_length
            b'\x01\x00'         # file_index
            b'\x77'             # pulse_count
            b'\x01'             # digitizer

            # Raster 2
            b'\x01\x01\x00\x00' # time_seconds
            b'\x02\x01\x00\x00' # time_fraction
            b'\x03\x01\x00\x00' # record_offset
            b'\x04\x01\x00\x00' # record_length
            b'\x02\x00'         # file_index
            b'\x00'             # pulse_count
            b'\x00'             # digitizer

            # Raster 3
            b'\x01\x00\x01\x00' # time_seconds
            b'\x02\x00\x01\x00' # time_fraction
            b'\x03\x00\x01\x00' # record_offset
            b'\x04\x00\x01\x00' # record_length
            b'\x02\x00'         # file_index
            b'\xA0'             # pulse_count
            b'\x01'             # digitizer

            # Files
            b'\x09\x00' b'first.tld'
            b'\x0A\x00' b'second.tld'
        )
        self.records = [
            {
                'record_offset': 3,
                'record_length': 4,
                'file_name': 'first.tld',
                'pulse_count': 119,
                'digitizer': 1,
                'time': 1.0000032000000001,
            },
            {
                'record_offset': 259,
                'record_length': 260,
                'file_name': 'second.tld',
                'pulse_count': 0,
                'digitizer': 0,
                'time': 257.00041279999999,
            },
            {
                'record_offset': 65539,
                'record_length': 65540,
                'file_name': 'second.tld',
                'pulse_count': 160,
                'digitizer': 1,
                'time': 65537.104860799998,
            },
        ]

    def test_decode(self):
        records = edb.decode(self.raw)
        self.assertEqual(records, self.records)

    def test_encode(self):
        raw = edb.encode(self.records)
        self.assertEqual(raw, self.raw)
