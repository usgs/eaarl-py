# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
'''
Useful constants for EAARL processing.

.. data:: refractive_index_air

    Refractive index of air

.. data:: refractive_index_water

    Refractive index of water

.. data:: speed_of_light_air

    Speed of light through air, in meters per second

.. data:: speed_of_light_water

    Speed of light through water, in meters per second
'''

# Boilerplate for cross-compatibility of Python 2/3
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future.builtins import * # pylint: disable=wildcard-import
import future.standard_library
future.standard_library.install_aliases()

import scipy.constants

# pylint: disable=invalid-name

refractive_index_air = 1.000276
refractive_index_water = 1.333

speed_of_light_air = scipy.constants.speed_of_light / refractive_index_air
speed_of_light_water = scipy.constants.speed_of_light / refractive_index_water
