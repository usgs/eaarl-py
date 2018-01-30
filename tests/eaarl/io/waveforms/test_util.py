from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
from future.builtins import *

import unittest

import numpy as np

from eaarl.io.waveforms import _util as util

DRIFT_INTERVAL = 1e-04

class TestTimeIntToSoe(unittest.TestCase):
    def test_sanity(self):
        util.time_int_to_soe(0, 0)

    def test_zero(self):
        soe = util.time_int_to_soe(0, 0)
        self.assertAlmostEqual(soe, 0., places=8)

    def test_seconds(self):
        soe = util.time_int_to_soe(123456789, 0)
        self.assertAlmostEqual(soe, 123456789., places=8)

    def test_fraction(self):
        soe = util.time_int_to_soe(0, 312500)
        self.assertAlmostEqual(soe, 0.5, places=8)

    def test_both(self):
        soe = util.time_int_to_soe(24680, 62500)
        self.assertAlmostEqual(soe, 24680.1, places=8)

    def test_numpy(self):
        seconds = np.array([100,200,300])
        fraction = np.array([6250, 9375, 12500])
        soe = util.time_int_to_soe(seconds, fraction)
        exp = np.array([100.01, 200.015, 300.02])
        np.testing.assert_almost_equal(soe, exp, 7)

class TestTimeSoeToInt(unittest.TestCase):
    def test_sanity(self):
        util.time_soe_to_int(0.)

    def test_zero(self):
        seconds, fraction = util.time_soe_to_int(0.)
        self.assertEqual(seconds, 0)
        self.assertEqual(fraction, 0)

    def test_seconds(self):
        seconds, fraction = util.time_soe_to_int(123456789.)
        self.assertEqual(seconds, 123456789)
        self.assertEqual(fraction, 0)

    def test_fraction(self):
        seconds, fraction = util.time_soe_to_int(0.5)
        self.assertEqual(seconds, 0)
        self.assertEqual(fraction, 312500)

    def test_both(self):
        seconds, fraction = util.time_soe_to_int(24680.1)
        self.assertEqual(seconds, 24680)
        self.assertEqual(fraction, 62500)

    def test_numpy(self):
        soe = np.array([100.01, 200.015, 300.02])
        seconds, fraction = util.time_soe_to_int(soe)
        exp_sec = np.array([100,200,300])
        exp_fra = np.array([6250, 9375, 12500])
        np.testing.assert_equal(seconds, exp_sec)
        np.testing.assert_equal(fraction, exp_fra)

class TestTimeDrift(unittest.TestCase):
    def test_drift(self):
        soe1 = np.arange(2000000000., 2000000001., DRIFT_INTERVAL)
        seconds1, fraction1 = util.time_soe_to_int(soe1)
        soe2 = util.time_int_to_soe(seconds1, fraction1)
        seconds2, fraction2 = util.time_soe_to_int(soe2)
        np.testing.assert_equal(seconds1, seconds2)
        np.testing.assert_equal(fraction1, fraction2)
        delta = np.absolute(soe1 - soe2)
        self.assertLessEqual(delta.max(), 8e-07)

class TestScanToDegrees(unittest.TestCase):
    def test_sanity(self):
        util.scan_counts_to_degrees(0)

    def test_zero(self):
        degrees = util.scan_counts_to_degrees(0)
        self.assertAlmostEqual(degrees, 0)

    def test_val(self):
        degrees = util.scan_counts_to_degrees(100)
        self.assertAlmostEqual(degrees, 4.5)

    def test_numpy(self):
        counts = np.array([100, 200, 300])
        degrees = util.scan_counts_to_degrees(counts)
        exp = np.array([4.5, 9.0, 13.5])
        np.testing.assert_almost_equal(degrees, exp)

class TestScanToCounts(unittest.TestCase):
    def test_sanity(self):
        util.scan_degrees_to_counts(0.)

    def test_zero(self):
        counts = util.scan_degrees_to_counts(0)
        self.assertAlmostEqual(counts, 0)

    def test_val(self):
        counts = util.scan_degrees_to_counts(4.5)
        self.assertAlmostEqual(counts, 100)

    def test_numpy(self):
        degrees = np.array([4.5, 9.0, 13.5])
        counts = util.scan_degrees_to_counts(degrees)
        exp = np.array([100, 200, 300])
        np.testing.assert_almost_equal(counts, exp)

class TestScanDrift(unittest.TestCase):
    def test_drift(self):
        deg1 = np.arange(-30., 30., DRIFT_INTERVAL)
        cnt1 = util.scan_degrees_to_counts(deg1)
        deg2 = util.scan_counts_to_degrees(cnt1)
        cnt2 = util.scan_degrees_to_counts(deg2)
        np.testing.assert_equal(cnt1, cnt2)
        delta = np.absolute(deg1 - deg2)
        self.assertLessEqual(delta.max(), 0.0225)
