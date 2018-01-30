# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
'''Handling for a collection of TLD waveform data

Module contents:
    * open
    * rasters_to_pulses
    * pulses_to_channels
    * EaarlCollection
'''

from __future__ import absolute_import

from .collection import collection_open as open # pylint: disable=redefined-builtin
from .collection import EaarlCollection
from .collection import rasters_to_pulses
from .collection import pulses_to_waveforms
from .collection import rasters_tx_clean
from .collection import rasters_wf_flip
