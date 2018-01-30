# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
'''Handling for EDB files'''

# Boilerplate for cross-compatibility of Python 2/3
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future.builtins import * # pylint: disable=wildcard-import
import future.standard_library
future.standard_library.install_aliases()

import struct

from ._types import EDBHeader, EDBRecord

# pylint: disable=no-member

####

def _unpack_pascal_string(buffer, offset):
    '''Unpack a string from the buffer'''
    length = struct.unpack_from('<H', buffer, offset)[0]
    offset += 2
    raw = buffer[offset:offset+length]
    return raw.decode('ascii')

def _unpack_pascal_strings(buffer, offset, count):
    '''Unpacks the specified number of strings from the buffer'''
    strings = []
    for _ in range(count):
        string = _unpack_pascal_string(buffer, offset)
        strings.append(string)
        offset += len(string) + 2
    return strings

def _pack_pascal_string(string):
    '''Pack the given string to a buffer'''
    buf = bytearray(2)
    struct.pack_into('<H', buf, 0, len(string))
    buf += string.encode('ascii')
    return buf

def _pack_pascal_strings(strings):
    '''Pack the given strings into a buffer'''
    buf = bytearray()
    for string in strings:
        buf += _pack_pascal_string(string)
    return buf

####

def decode(raw):
    '''Decode a raw buffer into EDB records
    '''
    offset = 0

    header = EDBHeader._unpack_from(raw, offset)
    offset += EDBHeader._size

    records = []
    for _ in range(header.record_count):
        records.append(EDBRecord._unpack_from(raw, offset))
        offset += EDBRecord._size

    files = _unpack_pascal_strings(raw, offset, header.file_count)

    result = []
    for record in records:
        record = record._asdict()
        record['file_name'] = files[record['file_index']-1]
        del record['file_index']
        result.append(record)

    return result

def encode(data):
    '''Encode a sequence of EDB records into a buffer
    '''
    # Make a sorted list of files referenced
    files = set()
    for record in data:
        files.add(record['file_name'])
    files = sorted(files)

    # Create a list of EDBRecord
    records = []
    for record in data:
        record = dict(record)
        record['file_index'] = files.index(record['file_name']) + 1
        del record['file_name']
        records.append(EDBRecord._fromdict(record))

    # Create EDBHeader
    files_offset = EDBHeader._size + EDBRecord._size * len(records)
    record_count = len(records)
    file_count = len(files)
    header = EDBHeader(files_offset, record_count, file_count)

    # Pack header as bytes
    buf = bytearray(files_offset)
    offset = 0
    header._pack_into(buf, 0)
    offset += EDBHeader._size

    # Pack records as bytes
    for record in records:
        record._pack_into(buf, offset)
        offset += EDBRecord._size

    # Pack files as bytes
    buf += _pack_pascal_strings(files)

    return buf

####

def read(f):
    '''Read records from an open file object'''
    raw = f.read()
    return decode(raw)

def read_from(filename, mode='rb'):
    '''Read records from a file specified by name'''
    with open(filename, mode) as f:
        return read(f)

def write(f, records):
    '''Write records to an open file object'''
    raw = encode(records)
    f.write(raw)

def write_to(filename, records, mode='wb'):
    '''Write records to a file specified by name'''
    with open(filename, mode) as f:
        write(f, records)
