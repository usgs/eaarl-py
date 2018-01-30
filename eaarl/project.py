# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
'''Geometry for mirror and target projection'''

# Boilerplate for cross-compatibility of Python 2/3
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future.builtins import * # pylint: disable=wildcard-import
import future.standard_library
future.standard_library.install_aliases()

import math

import numpy as np
from scipy.constants import nano
from .constants import speed_of_light_air

from .io.waveforms._util import scan_counts_to_degrees

def target_range(base_range, tx_pos, rx_pos, channel, ops):
    '''Calculate range from mirror to target

    Parameters
        base_range : array-like of integer
            Nanoseconds from start of transmit waveform to return waveform
            (i.e., frame.range)
        tx_pos : array-like of float
            Position in transmit of center of energy
        rx_pos : array-like of float
            Position in return of target center of energy
        channel : array-like of integer
            Channel of point
        ops : dict
            The ops conf data from the flight

    Returns : float
        Distance from mirror to target, in meters.
    '''
    range_bias = np.array(
        [ops['chn{0}_range_bias'.format(chan)] for chan in channel])
    samples = base_range + rx_pos - tx_pos + range_bias
    distance = samples * nano * speed_of_light_air * 0.5
    return distance - ops['range_biasM']

def project_mirror(frame, ops):
    '''Calculate mirror position

    Adds the mirror position to the frame DataFrame as mir_x, mir_y, and
    mir_z.

    Parameters
        frame : pandas.DataFrame
            A DataFrame containing the pulse records.
        ops : dict
            The ops conf data from the flight
    '''
    R_ar = _frame_rotation_aircraft(frame, ops)
    s_gm = np.array([ops['x_offset'], ops['y_offset'], ops['z_offset']])
    p_g = np.array([frame.ins_east, frame.ins_north, frame.ins_alt]).T

    p_m = _calc_mirror(R_ar, s_gm, p_g)
    frame['mir_x'] = p_m[:, 0]
    frame['mir_y'] = p_m[:, 1]
    frame['mir_z'] = p_m[:, 2]

def project_point(frame, ops, r_mt, coord_prefix=''):
    '''Calculate the target point position

    Adds the target position to the frame DataFrame as x, y, and z, with the
    prefix prepended if provided.

    Parameters
        frame : pandas.DataFrame
            A DataFrame containing the pulse records.
        ops : dict
            The ops conf data from the flight
        r_mt : array-like of float
            Distance from mirror to target, in meters
        coord_prefix : string
            A prefix to prepend to x, y, and z when adding the target
            coordinates to the DataFrame. The prefix will have _ added if
            missing. For example, if ``coord_prefix='fs'``, then the target
            coordinates will be added as 'fs_x', 'fs_y', and 'fs_z'.
    '''
    R_ar = _frame_rotation_aircraft(frame, ops)
    p_m = np.array([frame.mir_x, frame.mir_y, frame.mir_z]).T

    broadcast = lambda val: np.array(np.broadcast_to(val, frame.mir_x.shape))

    t_la_z = broadcast(0.)
    t_la_x = broadcast(45. - 0.4)
    t_ma_z = broadcast(0.)
    t_ma_x = broadcast(-22.5)
    t_ma_y = broadcast(frame.scan_angle +
                       scan_counts_to_degrees(ops['scan_bias']))

    t_ma_y, t_la_x = _spacing(t_ma_y, t_la_x, frame.channel, ops)

    dv_i = _calc_incidence(R_ar, t_la_z, t_la_x)
    dv_n = _calc_normal(R_ar, t_ma_z, t_ma_x, t_ma_y)
    del R_ar
    dv_s = _calc_reflection(dv_i, dv_n)
    del dv_i, dv_n
    p_t = _calc_target(dv_s, r_mt, p_m)

    if coord_prefix and coord_prefix[-1:] != '_':
        coord_prefix += '_'

    frame[coord_prefix + 'x'] = p_t[:, 0]
    frame[coord_prefix + 'y'] = p_t[:, 1]
    frame[coord_prefix + 'z'] = p_t[:, 2]

def _spacing(t_ma_y, t_la_x, channels, ops):
    '''Adjusts the angles for the EAARL-B target spacing

    Returns the adjusted (t_ma_y, t_la_x). The angles are adjusted to account
    for the EAARL-B target spacing.

    Parameters
        t_ma_y : array-like of float
            Array of mirror y-axis rotations, in degrees
        t_la_x : array-like of float
            Array of laser x-axis rotations, in degrees
        channels : array-like of integer
            Channel of point
        ops : dict
            The ops conf data from the flight
    '''
    if 'delta_ht' not in ops:
        return t_ma_y, t_la_x

    dz = ops['delta_ht']

    for channel in np.unique(channels):
        where = np.array(int(channel) == channels)

        dx = ops['chn{0}_dx'.format(channel)]
        dy = ops['chn{0}_dy'.format(channel)]

        if dx != 0 and dz != 0:
            tx = math.degrees(math.atan2(dx, dz))
            t_ma_y[where] -= tx

        if dy != 0 and dz != 0:
            ty = math.degrees(math.atan2(dy, dz))
            t_la_x[where] -= ty

    return t_ma_y, t_la_x

def _frame_rotation_aircraft(frame, ops):
    '''Returns rotation matrix for the aircraft'''
    t_ar_z = -frame.ins_heading + ops['yaw_bias']
    t_ar_x = frame.ins_pitch + ops['pitch_bias']
    t_ar_y = frame.ins_roll + ops['roll_bias']
    return _rotation_aircraft(t_ar_z, t_ar_x, t_ar_y)

def _rotation_aircraft(t_ar_z, t_ar_x, t_ar_y):
    '''Returns rotation matrx for the aircraft'''
    t_ar_x_rad = np.deg2rad(t_ar_x)
    cos_x = np.cos(t_ar_x_rad)
    sin_x = np.sin(t_ar_x_rad)
    del t_ar_x_rad

    t_ar_y_rad = np.deg2rad(t_ar_y)
    cos_y = np.cos(t_ar_y_rad)
    sin_y = np.sin(t_ar_y_rad)
    del t_ar_y_rad

    t_ar_z_rad = np.deg2rad(t_ar_z)
    cos_z = np.cos(t_ar_z_rad)
    sin_z = np.sin(t_ar_z_rad)
    del t_ar_z_rad

    sin_x_sin_y = sin_x * sin_y
    cos_y_cos_z = cos_y * cos_z
    cos_y_sin_z = cos_y * sin_z

    R_ar = np.zeros(cos_x.shape + (3, 3))

    R_ar[..., 0, 0] = cos_y_cos_z - sin_z * sin_x_sin_y
    R_ar[..., 0, 1] = - sin_z * cos_x
    R_ar[..., 0, 2] = cos_z * sin_y + cos_y_sin_z * sin_x

    R_ar[..., 1, 0] = cos_y_sin_z + cos_z * sin_x_sin_y
    R_ar[..., 1, 1] = cos_x * cos_z
    R_ar[..., 1, 2] = sin_y * sin_z - cos_y_cos_z * sin_x

    R_ar[..., 2, 0] = - cos_x * sin_y
    R_ar[..., 2, 1] = sin_x
    R_ar[..., 2, 2] = cos_x * cos_y

    return R_ar

def _calc_mirror(R_ar, s_gm, p_g):
    '''Calculates the mirror position'''
    p_m = np.zeros(p_g.shape)

    p_m[..., 0] = (
        p_g[..., 0] +
        R_ar[..., 0, 0] * s_gm[..., 0] +
        R_ar[..., 0, 1] * s_gm[..., 1] +
        R_ar[..., 0, 2] * s_gm[..., 2]
    )
    p_m[..., 1] = (
        p_g[..., 1] +
        R_ar[..., 1, 0] * s_gm[..., 0] +
        R_ar[..., 1, 1] * s_gm[..., 1] +
        R_ar[..., 1, 2] * s_gm[..., 2]
    )
    p_m[..., 2] = (
        p_g[..., 2] +
        R_ar[..., 2, 0] * s_gm[..., 0] +
        R_ar[..., 2, 1] * s_gm[..., 1] +
        R_ar[..., 2, 2] * s_gm[..., 2]
    )

    return p_m

def _calc_incidence(R_ar, t_la_z, t_la_x):
    '''Calculates the laser angle of incidence'''
    sin = lambda theta: np.sin(theta)[..., np.newaxis]
    cos = lambda theta: np.cos(theta)[..., np.newaxis]

    x = np.deg2rad(t_la_x)
    z = np.deg2rad(t_la_z)

    dv_i = (
        R_ar[..., 0] * sin(z) -
        R_ar[..., 1] * cos(z)
    )
    dv_i *= cos(x)
    dv_i -= R_ar[..., 2] * sin(x)

    return dv_i

def _calc_normal(R_ar, t_ma_z, t_ma_x, t_ma_y):
    '''Calculates the laser normal angle'''
    t_ma_x_rad = np.deg2rad(np.broadcast_to(np.array(t_ma_x), R_ar.shape[:-2]))
    cos_x = np.cos(t_ma_x_rad)
    sin_x = np.sin(t_ma_x_rad)
    del t_ma_x_rad

    t_ma_y_rad = np.deg2rad(np.broadcast_to(np.array(t_ma_y), R_ar.shape[:-2]))
    cos_y = np.cos(t_ma_y_rad)
    sin_y = np.sin(t_ma_y_rad)
    del t_ma_y_rad

    t_ma_z_rad = np.deg2rad(np.broadcast_to(np.array(t_ma_z), R_ar.shape[:-2]))
    cos_z = np.cos(t_ma_z_rad)
    sin_z = np.sin(t_ma_z_rad)
    del t_ma_z_rad

    sin_x_cos_y = sin_x * cos_y

    dv_n = R_ar[..., 0] * (
        (sin_y * cos_z) + (sin_x_cos_y * sin_z)
    )[:, np.newaxis]
    dv_n += R_ar[..., 1] * (
        sin_y * sin_z - sin_x_cos_y * cos_z
    )[:, np.newaxis]
    dv_n += R_ar[..., 2] * (cos_x * cos_y)[:, np.newaxis]

    return dv_n

def _calc_reflection(dv_i, dv_n):
    '''Calculates the laser reflection angle'''
    return 2 * np.sum(dv_i * dv_n, axis=-1, keepdims=True) * dv_n - dv_i

def _calc_target(dv_s, r_mt, p_m):
    '''Calculates the target position'''
    return dv_s * np.array(r_mt)[..., np.newaxis] + p_m
