from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
from future.builtins import *

from unittest import TestCase

from eaarl.io.waveforms import _types as types

class TestEDBHeader(TestCase):
    '''Test both EDBHeader and the underlying _namedtuple_struct

    This is the simplest class that uses _namedtuple_struct, so EDBHeader is
    tested more thoroughly than some of the other classes.
    '''
    def test_sanity(self):
        header = types.EDBHeader(1,2,3)

    def test_files_offset(self):
        header = types.EDBHeader(42,0,0)
        self.assertEqual(header.files_offset, 42)

    def test_record_count(self):
        header = types.EDBHeader(0,42,0)
        self.assertEqual(header.record_count, 42)

    def test_file_count(self):
        header = types.EDBHeader(0,0,42)
        self.assertEqual(header.file_count, 42)

    def test_tuple(self):
        header = types.EDBHeader(1,2,3)
        self.assertEqual(header, (1,2,3))

    def test_fromdict(self):
        header = types.EDBHeader._fromdict({
            'files_offset': 3,
            'record_count': 2,
            'file_count': 1,
        })
        self.assertEqual(header, (3,2,1))

    def test_asdict(self):
        header = types.EDBHeader(1,2,3)
        expected = {
            'files_offset': 1,
            'record_count': 2,
            'file_count': 3,
        }
        self.assertEqual(header._asdict(), expected)

    def test_unpack(self):
        raw = b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C'
        header = types.EDBHeader._unpack(raw)
        self.assertEqual(header, (67305985, 134678021, 202050057))

    def test_unpack_from(self):
        raw = b'\x10\x11\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x20\x21'
        header = types.EDBHeader._unpack_from(raw, offset=2)
        self.assertEqual(header, (67305985, 134678021, 202050057))

    def test_pack(self):
        raw = b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C'
        header = types.EDBHeader(67305985, 134678021, 202050057)
        self.assertEqual(header._pack(), raw)

    def test_pack_into(self):
        raw = b'\x10\x11\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x20\x21'
        buf = bytearray(
            b'\x10\x11\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3A\x3B\x3C\x20\x21')
        header = types.EDBHeader(67305985, 134678021, 202050057)
        header._pack_into(buf, 2)
        self.assertEqual(buf, raw)

    def test_replace_files_offset(self):
        header = types.EDBHeader(1,2,3)
        header = header._replace(files_offset=42)
        self.assertEqual(header, (42,2,3))

    def test_replace_record_count(self):
        header = types.EDBHeader(1,2,3)
        header = header._replace(record_count=42)
        self.assertEqual(header, (1,42,3))

    def test_replace_file_count(self):
        header = types.EDBHeader(1,2,3)
        header = header._replace(file_count=42)
        self.assertEqual(header, (1,2,42))

    def test_replace_all(self):
        header = types.EDBHeader(1,2,3)
        header = header._replace(files_offset=10, record_count=20,
                                 file_count=30)
        self.assertEqual(header, (10, 20, 30))

class ToFromDict(TestCase):
    cls = None
    tup = None
    dct = None

    def test_sanity(self):
        self.cls(*self.tup)

    def test_fromdict(self):
        # Force a copy to avoid modifying class copy
        dct = dict(self.dct)
        val = self.cls._fromdict(dct)
        self.assertEqual(tuple(val), self.tup)

    def test_todict(self):
        val = self.cls(*self.tup)._asdict()
        self.assertEqual(val, self.dct)

class TestEDBRecord(ToFromDict):
    cls = types.EDBRecord
    tup = (1,2,3,4,5,6,7)
    dct = {
        'time': 1.0000032,
        'record_offset': 3,
        'record_length': 4,
        'file_index': 5,
        'pulse_count': 6,
        'digitizer': 7,
    }

class TestTLDRecordHeader(ToFromDict):
    cls = types.TLDRecordHeader
    tup = (84083201,)
    dct = {
        'record_length': 197121,
        'record_type': 5,
    }

class TestTLDRasterHeader(ToFromDict):
    cls = types.TLDRasterHeader
    tup = (6,2,3,32770)
    dct = {
        'time': 6.0000032,
        'raster_number': 3,
        'digitizer': 1,
        'pulse_count': 2,
    }

class TestTLDPulseHeader(ToFromDict):
    cls = types.TLDPulseHeader
    tup = (67305985,5,6,7,8,9,2826,3340)
    dct = {
        'time_offset': 0.3153936,
        'waveform_count': 4,
        'scan_angle': 127.17,
        'range': 3340,
        'thresh_tx': 0,
        'thresh_rx': 0,
        'bias_tx': 5,
        'bias_rx': [6,7,8,9],
    }

# Delete class so that it isn't treated as actual tests
del ToFromDict
