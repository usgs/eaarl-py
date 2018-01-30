# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
'''Data types for waveform files'''

# Boilerplate for cross-compatibility of Python 2/3
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future.builtins import * # pylint: disable=wildcard-import
import future.standard_library
future.standard_library.install_aliases()

from collections import namedtuple
from struct import Struct

from . import _util as util

# pylint: disable=no-member,too-few-public-methods

def _set_doc(fnc, tokens, doc):
    '''Set the docstring for a method

    Python 2 and Python 3 have slightly different semantics for setting the
    docstring on methods. This encapsulates those differences. It also handles
    formatting and cleanup of the docstring.

    tokens should be dict containing the replacements to apply to doc. doc
    should be the docstring to apply to fnc. fnc should be a method or class
    method.'''
    doc = doc.strip().format(**tokens)
    try:
        fnc.__doc__ = doc
    except AttributeError:
        fnc.__func__.__doc__ = doc

def _namedtuple_struct(typename, fmt, fields, doc=None):
    '''Creates a class combining struct.Struct and collections.namedtuple

    The class will be subclassed from a namedtuple. The namedtuple class's name
    will be the given typename with 'Tuple' appended.

    The subclass wraps around the Struct functionality. It provides class
    attribute _size, class methods _unpack and _unpack_from, and instance
    methods _pack and _pack_into that all map to corresponding Struct
    attributes/methods.

    The subclass also adds a convenience _fromdict classmethod to complement
    the _make method provided by namedtuple.
    '''
    tupletypename = typename + 'Tuple'
    tupletype = namedtuple(tupletypename, fields)

    signature = typename + '(' + ', '.join(fields) + ')'

    if doc is None:
        doc = signature

    @classmethod
    def _fromdict(cls, dct):
        vals = [dct[f] for f in cls._fields]
        return cls(*vals)

    def _pack(self):
        return self._struct.pack(*tuple(self))

    def _pack_into(self, buffer, offset):
        return self._struct.pack_into(buffer, offset, *tuple(self))

    @classmethod
    def _unpack(cls, string):
        vals = cls._struct.unpack(string)
        return cls(*vals)

    @classmethod
    def _unpack_from(cls, buffer, offset=0):
        vals = cls._struct.unpack_from(buffer, offset)
        return cls(*vals)

    _repr = typename + '(' + ', '.join([f+'=%r' for f in fields]) + ')'
    def __repr__(self):
        '''Return a nicely formatted representation string'''
        return _repr % self

    _struct = Struct(fmt)

    defs = {
        '__doc__': doc,
        '__slots__': (),
        '__repr__': __repr__,
        '_struct': _struct,
        '_size': _struct.size,
        '_fromdict': _fromdict,
        '_pack': _pack,
        '_pack_into': _pack_into,
        '_unpack': _unpack,
        '_unpack_from': _unpack_from,
    }

    # pylint: disable=invalid-name
    try:
        _NamedTuplePacker = type(typename, (tupletype,), defs)
    except TypeError:
        _NamedTuplePacker = type(typename.encode('ascii'), (tupletype,), defs)
    # pylint: enable=invalid-name

    def _asdict(self):
        'Return a new dict which maps field names to their values'
        return dict(super(_NamedTuplePacker, self)._asdict())
    _NamedTuplePacker._asdict = _asdict

    tokens = {
        'signature': signature,
        'typename': typename,
    }

    # Inherited methods

    _set_doc(_NamedTuplePacker.__new__, tokens, '''
    Create a new instance of {signature}
    ''')

    _set_doc(_NamedTuplePacker._make, tokens, '''
    Make a new {typename} object from a sequence or iterable
    ''')

    _set_doc(_NamedTuplePacker._replace, tokens, '''
    Return a new {typename} object replacing specified fields with new values
    ''')

    # Local methods
    _set_doc(_NamedTuplePacker._fromdict, tokens, '''
    Make a new {typename} object from a dict
    ''')

    _set_doc(_NamedTuplePacker._unpack, tokens, '''
    Make a new {typename} object by unpacking a raw bytestring

    Requires len(str) == {typename}._size
    ''')

    _set_doc(_NamedTuplePacker._unpack_from, tokens, '''
    Make a new {typename} object by unpacking a raw bytestring

    Requires len(buffer[offset:]) >= self._size
    ''')

    _set_doc(_NamedTuplePacker._pack, tokens, '''
    Return a string containing the {typename} object's packed data
    ''')

    _set_doc(_NamedTuplePacker._pack_into, tokens, '''
    Pack the {typename} object's data into the given buffer

    The given buffer must be writable. The packed data will be written starting
    at the the given offset.
    ''')

    return _NamedTuplePacker

################

# pylint: disable=invalid-name

EDBHeader = _namedtuple_struct('EDBHeader', '<3L',
                               ('files_offset', 'record_count', 'file_count'))

EDBRecordBase = _namedtuple_struct('EDBRecord', '<4Lh2B',
                                   ('time_seconds', 'time_fraction',
                                    'record_offset', 'record_length',
                                    'file_index', 'pulse_count', 'digitizer'))

TLDRecordHeaderBase = _namedtuple_struct('TLDRecordHeader', '<L',
                                         ('length_type',))

TLDRasterHeaderBase = _namedtuple_struct('TLDRasterHeader', '<3LH',
                                         ('time_seconds', 'time_fraction',
                                          'raster_number',
                                          'digitizer_pulse_count'))

TLDPulseHeaderBase = _namedtuple_struct('TLDPulseHeader', '<L5BhH',
                                        ('time_offset_waveform_count',
                                         'bias_tx', 'bias_rx_1', 'bias_rx_2',
                                         'bias_rx_3', 'bias_rx_4',
                                         'scan_angle_counts', 'range_thresh'))

# pylint: enable=invalid-name

################

def _rshift_and(val, shift, _and):
    mask = 2 ** _and - 1
    val >>= shift
    val &= mask
    return val

def _lshift_and(val, shift, _and):
    mask = 2 ** _and - 1
    val &= mask
    val <<= shift
    return val

def _bits_unwrap(dct, conf):
    for src, dst, shift, bits in conf:
        dct[dst] = _rshift_and(dct[src], shift, bits)
    for src, _, _, _ in conf:
        try:
            del dct[src]
        except KeyError:
            pass

def _bits_wrap(dct, conf):
    for dst, _, _, _ in conf:
        dct[dst] = 0
    for dst, src, shift, bits in conf:
        dct[dst] |= _lshift_and(dct[src], shift, bits)
    for _, src, _, _ in conf:
        del dct[src]

def _time_to_int(dct, src, dst_seconds, dst_fraction):
    seconds, fraction = util.time_soe_to_int(dct[src])
    del dct[src]

    if dst_seconds is not None:
        dct[dst_seconds] = seconds
    dct[dst_fraction] = fraction

def _time_to_soe(dct, dst, src_seconds, src_fraction):
    if src_seconds is None:
        seconds = 0
    else:
        seconds = dct[src_seconds]
        del dct[src_seconds]
    fraction = dct[src_fraction]
    del dct[src_fraction]

    dct[dst] = util.time_int_to_soe(seconds, fraction)

################

class EDBRecord(EDBRecordBase):
    '''Record in EDB file'''
    @classmethod
    def _fromdict(cls, dct):
        _time_to_int(dct, 'time', 'time_seconds', 'time_fraction')
        return super(EDBRecord, cls)._fromdict(dct)

    def _asdict(self):
        dct = super(EDBRecord, self)._asdict()
        _time_to_soe(dct, 'time', 'time_seconds', 'time_fraction')
        return dct

class TLDRecordHeader(TLDRecordHeaderBase):
    '''Record header in TLD file'''
    _bits_map = [
        ('length_type', 'record_type', 24, 8),
        ('length_type', 'record_length', 0, 24),
    ]

    @classmethod
    def _fromdict(cls, dct):
        _bits_wrap(dct, cls._bits_map)
        return super(TLDRecordHeader, cls)._fromdict(dct)

    def _asdict(self):
        dct = super(TLDRecordHeader, self)._asdict()
        _bits_unwrap(dct, self._bits_map)
        return dct

class TLDRasterHeader(TLDRasterHeaderBase):
    '''Raster header in record of TLD file'''
    _bits_map = [
        ('digitizer_pulse_count', 'digitizer', 15, 1),
        ('digitizer_pulse_count', 'pulse_count', 0, 15),
    ]

    @classmethod
    def _fromdict(cls, dct):
        _time_to_int(dct, 'time', 'time_seconds', 'time_fraction')
        _bits_wrap(dct, cls._bits_map)
        return super(TLDRasterHeader, cls)._fromdict(dct)

    def _asdict(self):
        dct = super(TLDRasterHeader, self)._asdict()
        _bits_unwrap(dct, self._bits_map)
        _time_to_soe(dct, 'time', 'time_seconds', 'time_fraction')
        return dct

class TLDPulseHeader(TLDPulseHeaderBase):
    '''Pulse header for pulse in raster of TLD file'''
    _bits_map = [
        ('time_offset_waveform_count', 'waveform_count', 24, 8),
        ('time_offset_waveform_count', 'time_fraction', 0, 24),
        ('range_thresh', 'thresh_rx', 15, 1),
        ('range_thresh', 'thresh_tx', 14, 1),
        ('range_thresh', 'range', 0, 14),
    ]

    @classmethod
    def _fromdict(cls, dct):
        _time_to_int(dct, 'time_offset', None, 'time_fraction')
        _bits_wrap(dct, cls._bits_map)

        dct['bias_rx_1'] = dct['bias_rx'][0]
        dct['bias_rx_2'] = dct['bias_rx'][1]
        dct['bias_rx_3'] = dct['bias_rx'][2]
        dct['bias_rx_4'] = dct['bias_rx'][3]
        del dct['bias_rx']

        dct['scan_angle_counts'] = \
                util.scan_degrees_to_counts(dct['scan_angle'])
        del dct['scan_angle']

        return super(TLDPulseHeader, cls)._fromdict(dct)

    def _asdict(self):
        dct = super(TLDPulseHeader, self)._asdict()

        _bits_unwrap(dct, self._bits_map)
        _time_to_soe(dct, 'time_offset', None, 'time_fraction')

        dct['bias_rx'] = [dct['bias_rx_1'], dct['bias_rx_2'], dct['bias_rx_3'],
                          dct['bias_rx_4']]
        del dct['bias_rx_1']
        del dct['bias_rx_2']
        del dct['bias_rx_3']
        del dct['bias_rx_4']

        dct['scan_angle'] = \
                util.scan_counts_to_degrees(dct['scan_angle_counts'])
        del dct['scan_angle_counts']

        return dct
