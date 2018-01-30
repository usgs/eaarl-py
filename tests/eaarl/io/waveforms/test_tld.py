from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
from future.builtins import *

import copy
import unittest
from io import BytesIO

from eaarl.io.waveforms import tld

class TestTld(unittest.TestCase):
    def setUp(self):
        self.raw = [
            (
                b'\x3F\x00\x00'      # length
                b'\x05'              # type

                b'\x01\x02\x03\x04' # time_seconds
                b'\x00\x00\x00\x00' # time_fraction
                b'\x00\x00\x00\x00' # raster number
                b'\x02\x00'         # bitfield: pulse count, digitizer

                # pulse 0
                b'\x11\x12\x03'     # offset time
                b'\x01'             # waveform count
                b'\x00'             # transmit bias
                b'\x00\x00\x00\x00' # return biases
                b'\x00\x00'         # scan angle counts
                b'\x00\x00'         # bitfield: range, flags
                b'\x08\x00'         # data length
                b'\x02'             # tx length
                b'\x30\x31'         # tx waveform
                b'\x03\x00'         # rx 0 len
                b'\x40\x41\x42'     # rx 0 waveform

                # pulse 1
                b'\x21\x22\x03'     # offset time
                b'\x01'             # waveform count
                b'\x00'             # transmit bias
                b'\x00\x00\x00\x00' # return biases
                b'\x00\x00'         # scan angle counts
                b'\x00\x00'         # bitfield: range, flags
                b'\x07\x00'         # data length
                b'\x02'             # tx length
                b'\x52\x52'         # tx waveform
                b'\x02\x00'         # rx 0 len
                b'\x61\x62'         # rx 0 waveform
            ),
            (
                b'\x38\x00\x00'      # length
                b'\x05'              # type

                b'\x11\x12\x13\x14' # time_seconds
                b'\x00\x00\x00\x00' # time_fraction
                b'\x00\x00\x00\x00' # raster number
                b'\x01\x00'         # bitfield: pulse count, digitizer

                # pulse 0
                b'\x11\x12\x03'     # offset time
                b'\x04'             # waveform count
                b'\x00'             # transmit bias
                b'\x00\x00\x00\x00' # return biases
                b'\x00\x00'         # scan angle counts
                b'\x00\x00'         # bitfield: range, flags
                b'\x17\x00'         # data length
                b'\x02'             # tx length
                b'\x30\x31'         # tx waveform
                b'\x03\x00'         # rx 0 len
                b'\x40\x41\x42'     # rx 0 waveform
                b'\x03\x00'         # rx 1 len
                b'\x60\x61\x62'     # rx 1 waveform
                b'\x03\x00'         # rx 2 len
                b'\x70\x71\x72'     # rx 2 waveform
                b'\x03\x00'         # rx 3 len
                b'\x80\x81\x82'     # rx 3 waveform
            ),
        ]

        self.records = [
            {
                'time': 67305985,
                'raster_number': 0,
                'digitizer': 0,
                'pulse_count': 2,
                'pulse': [
                    {
                        'time': 67305985.3219728,
                        'waveform_count': 1,
                        'bias_tx': 0,
                        'bias_rx': [0,0,0,0],
                        'scan_angle': 0,
                        'range': 0,
                        'thresh_rx': 0,
                        'thresh_tx': 0,
                        'tx': [48, 49],
                        'rx': [
                            [64,65,66],
                        ],
                    },
                    {
                        'time': 67305985.328552,
                        'waveform_count': 1,
                        'bias_tx': 0,
                        'bias_rx': [0,0,0,0],
                        'scan_angle': 0,
                        'range': 0,
                        'thresh_rx': 0,
                        'thresh_tx': 0,
                        'tx': [82, 82],
                        'rx': [
                            [97, 98],
                        ],
                    },
                ],
            },
            {
                'time': 336794129,
                'raster_number': 0,
                'digitizer': 0,
                'pulse_count': 1,
                'pulse': [
                    {
                        'time': 336794129.3219728,
                        'waveform_count': 4,
                        'bias_tx': 0,
                        'bias_rx': [0,0,0,0],
                        'scan_angle': 0,
                        'range': 0,
                        'thresh_rx': 0,
                        'thresh_tx': 0,
                        'tx': [48, 49],
                        'rx': [
                            [64,65,66],
                            [96,97,98],
                            [112,113,114],
                            [128,129,130],
                        ],
                    },
                ],
            },
        ]

    def test_read_first(self):
        fh = BytesIO(self.raw[0] + self.raw[1])
        records = tld.read(fh, 0, 1)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0], self.records[0])

    def test_read_both(self):
        fh = BytesIO(self.raw[0] + self.raw[1])
        records = tld.read(fh, 0, 2)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0], self.records[0])
        self.assertEqual(records[1], self.records[1])

    def test_read_second(self):
        fh = BytesIO(self.raw[0] + self.raw[1])
        records = tld.read(fh, 63, 1)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0], self.records[1])

    def test_read_both_with_garbage(self):
        raw = bytearray(self.raw[0] + b'\xAA\xBB\xCC\xDD' + self.raw[1])
        raw[0] += 4
        fh = BytesIO(raw)
        records = tld.read(fh, 0, 2)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0], self.records[0])
        self.assertEqual(records[1], self.records[1])

    def test_write_first(self):
        fh = BytesIO()
        tld.write(fh, [self.records[0]])
        raw = fh.getvalue()
        self.assertEqual(raw, self.raw[0])

    def test_write_both(self):
        fh = BytesIO()
        tld.write(fh, self.records)
        raw = fh.getvalue()
        self.assertEqual(len(raw), len(self.raw[0]+self.raw[1]))
        self.assertEqual(raw, self.raw[0]+self.raw[1])

    def test_write_both_separately(self):
        fh = BytesIO()
        tld.write(fh, [self.records[0]])
        tld.write(fh, [self.records[1]])
        raw = fh.getvalue()
        self.assertEqual(len(raw), len(self.raw[0]+self.raw[1]))
        self.assertEqual(raw, self.raw[0]+self.raw[1])

    def test_write_pulse_count_optional(self):
        rec = copy.deepcopy(self.records[0])
        del rec['pulse_count']
        fh = BytesIO()
        tld.write(fh, [rec])
        raw = fh.getvalue()
        self.assertEqual(raw, self.raw[0])

    def test_write_waveform_count_optional(self):
        rec = copy.deepcopy(self.records[0])
        del rec['pulse'][0]['waveform_count']
        del rec['pulse'][1]['waveform_count']
        fh = BytesIO()
        tld.write(fh, [rec])
        raw = fh.getvalue()
        self.assertEqual(raw, self.raw[0])

