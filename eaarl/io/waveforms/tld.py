# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# pylint: disable = no-member
'''Handling for TLD data'''

# Boilerplate for cross-compatibility of Python 2/3
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future.builtins import * # pylint: disable=wildcard-import
import future.standard_library
future.standard_library.install_aliases()

import copy
import struct

from ._types import TLDRecordHeader, TLDRasterHeader, TLDPulseHeader

def read(f, offset, count, progress=None):
    '''Read records from file

    Parameters
        f : filehandle
            Open readable filehandle
        offset : int
            Offset into file to start reading at
        count : int
            Number of records to read
        progress : tqdm.tqdm or compatible or None or False
            If provided, then progress.update() will be called after each
            raster is loaded. This is intended to support display of a progress
            bar via tqdm.
    '''
    f.seek(offset)
    records = []
    for _ in range(count):
        records.append(_read_record(f))
        if progress:
            progress.update()
    return records

def _read_record(f):
    '''Read and return a raster record'''
    raw = f.read(TLDRecordHeader._size)
    record_header = TLDRecordHeader._unpack(raw)._asdict()
    data_length = record_header['record_length'] - TLDRecordHeader._size
    raw = f.read(data_length)

    if record_header['record_type'] != 5:
        return None

    raster = TLDRasterHeader._unpack_from(raw, 0)._asdict()
    raster['pulse'] = []
    offset = TLDRasterHeader._size
    for _ in range(raster['pulse_count']):
        pulse, offset = _read_pulse(raw, offset)
        pulse['time'] = raster['time'] + pulse['time_offset']
        del pulse['time_offset']
        raster['pulse'].append(pulse)

    return raster

def _read_pulse(raw, offset):
    '''read and return a pulse record'''
    pulse = TLDPulseHeader._unpack_from(raw, offset)._asdict()
    offset += TLDPulseHeader._size

    data_length = struct.unpack_from('<H', raw, offset)[0]
    offset += 2

    _read_waveforms(raw[offset:offset+data_length], pulse)
    offset += data_length

    return (pulse, offset)

def _read_waveforms(raw, pulse):
    '''Read and return a set of waveforms'''
    offset = 0

    length = struct.unpack_from('<B', raw, offset)[0]
    offset += 1
    pulse['tx'] = _wf(raw[offset:offset+length])
    offset += length

    pulse['rx'] = []
    for _ in range(pulse['waveform_count']):
        length = struct.unpack_from('<H', raw, offset)[0]
        offset += 2
        pulse['rx'].append(_wf(raw[offset:offset+length]))
        offset += length

def _wf(raw):
    '''Converts a buffer into an integer sequence'''
    return [_ for _ in bytes(raw)]

def write(f, rasters):
    '''Writes a series of rasters to an open filehandle'''
    for raster in rasters:
        f.write(_encode_record(raster))

def _encode_record(raster):
    '''Encode a raster into a buffer'''
    # Build up a bytestring with the data, then write it
    # Can't write as its generated since the record length comes first
    # Avoiding random-access in case f is write-only

    # Some modifications will be made later, ensure they don't alter the
    # originals
    raster = copy.deepcopy(raster)

    # Allocate the space for the record header, but wait to populate it
    buffer = bytearray(TLDRecordHeader._size)

    # Add the raster header
    raster['pulse_count'] = len(raster['pulse'])
    buffer += TLDRasterHeader._fromdict(copy.deepcopy(raster))._pack()

    for pulse in raster['pulse']:
        pulse['time_offset'] = pulse['time'] - raster['time']
        buffer += _encode_pulse(pulse)

    header = {'record_type': 5, 'record_length': len(buffer)}
    TLDRecordHeader._fromdict(header)._pack_into(buffer, 0)

    return buffer

def _encode_pulse(pulse):
    '''Encode a pulse into a buffer'''
    pulse['waveform_count'] = min(4, len(pulse['rx']))

    header = TLDPulseHeader._fromdict(pulse)._pack()
    waveforms = _encode_waveforms(pulse)

    return header + struct.pack('<H', len(waveforms)) + waveforms

def _encode_waveforms(pulse):
    '''Encode a set of waveforms into a buffer'''
    buffer = bytearray()

    buffer += struct.pack('<B', len(pulse['tx']))
    buffer += bytearray(pulse['tx'])

    for rx in pulse['rx']:
        buffer += struct.pack('<H', len(rx))
        buffer += bytearray(rx)

    return buffer
