# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
'''Random-consensus filter algorithms'''

# Boilerplate for cross-compatibility of Python 2/3
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future.builtins import * # pylint: disable=wildcard-import
import future.standard_library
future.standard_library.install_aliases()

import numpy as np

def rcf_jury(jury, width, tie=None):
    '''Find winning window of jury

    Parameters
        jury : array-like of numeric
            Jury of values to search for winning window
        width : numeric
            Search window
        tie : string or None
            Specifies how to handle a tie. Valid values:
                * 'high' or None - Uses the highest winning window
                * 'mid' - Uses the middle winning window
                * 'low' - Uses the lowest winning window
    '''
    jury = np.array(jury)
    jury.sort()

    best_vote = 0
    best_index = [0]

    i = j = 0
    while i < jury.size:
        lower = jury[i]
        upper = lower + width
        while j < jury.size and jury[j] < upper:
            j += 1
        vote = j - i
        if vote > best_vote:
            best_vote = vote
            best_index = [i]
        elif vote == best_vote:
            best_index.append(i)
        i += 1
        while i < jury.size and jury[i] == lower:
            i += 1

    if tie is None or tie == 'high':
        idx = best_index[-1]
    elif tie == 'low':
        idx = best_index[0]
    elif tie == 'mid':
        idx = best_index[int(len(best_index)/2.)]
    else:
        raise ValueError('invalid tie value')

    return jury[idx]

def rcf_grid(x, y, z, width, cell_size, min_winners=3, tie=None):
    '''Determines which points pass the gridded RCF filter

    Returns an array of Boolean values where True means a point passed the
    filter. The filter divides the points into cells based on cell_size, then
    finds points with elevation values that pass the RCF filter using the given
    width.

    Parameters
        x : array-like of floats
            x coordinates for points
        y : array-like of floats
            y coordinates for points
        z : array-like of floats
            z coordinates for points
        width : numeric
            Vertical search window to use in each cell
        cell_size : numeric
            Horizontal cell size
        min_winners : integer
            Minimum number of points needed for winning points to pass the
            filter in a grid cell
        tie : string or None
            Specifies how to handle a tie. Valid values:
                * 'high' or None - Uses the highest winning window
                * 'mid' - Uses the middle winning window
                * 'low' - Uses the lowest winning window
    '''
    bottom = lambda v: int(v.min() / cell_size) * cell_size
    grid_nums = lambda v: ((v - bottom(v))/cell_size).astype('int')

    xgrid = grid_nums(x)
    ygrid = grid_nums(y)

    xgrid_uniq = np.unique(xgrid)
    ygrid_uniq = np.unique(ygrid)

    keep = np.zeros_like(x, dtype='bool')

    where_and = lambda k1, k2: np.nonzero(np.logical_and(k1, k2))[0]

    for xgi in xgrid_uniq:
        for ygi in ygrid_uniq:
            idx = where_and(xgrid == xgi, ygrid == ygi)
            if idx.size == 0:
                continue

            low = rcf_jury(z[idx], width, tie=tie)
            good = idx[where_and(z[idx] >= low, z[idx] < low + width)]
            if good.size >= min_winners:
                keep[good] = True

    return keep
