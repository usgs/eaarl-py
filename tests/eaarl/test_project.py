# pylint: disable=missing-docstring,bad-whitespace,protected-access

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library # pylint: disable=unused-import
from future.builtins import *

import numpy as np
import numpy.testing as nptest

from eaarl import project

def test_rotation_aircraft():
    t_z = np.array([10,-22.5,0,119.3,-87.3])
    t_x = np.array([20,-8.7,3.1,33.33,-21.7])
    t_y = np.array([15,3.14,-18.11,-14.01,22.22])

    expected = np.array([
        [[0.9358796755,-0.1631759112,0.3122544717],
         [0.2549077485,0.9254165784,-0.2804036308],
         [-0.2432103468,0.3420201433,0.9076733712]],

        [[0.919321783,0.3782802335,0.1084044475],
         [-0.3897636561,0.91324927,0.1185751371],
         [-0.05414565203,-0.1512608202,0.9870098341]],

        [[0.9504614939,-0,-0.3108423212],
         [-0.01680998376,0.9985366703,-0.05139982938],
         [0.3103874564,0.05407881298,0.9490706554]],

        [[-0.3588227751,-0.7286311259,0.5833891484],
         [0.9112256834,-0.408888718,0.04977720541],
         [0.2022720198,0.5494603704,0.8106659801]],

        [[-0.09606141096,0.9281011182,0.3597228374],
         [-0.931297606,0.04376813768,-0.3616201311],
         [-0.3513644467,-0.3697467573,0.8601339204]],
    ])

    actual = project._rotation_aircraft(t_z, t_x, t_y)

    nptest.assert_allclose(actual, expected, rtol=0, atol=1e-7)

def test_calc_mirror():
    R_ar = np.array([
        [[1,0,0],
         [0,1,0],
         [0,0,1]],
        [[2,3,4],
         [5,6,7],
         [8,9,10]],
        [[2,3,4],
         [5,6,7],
         [8,9,10]],
    ])
    s_gm = np.array([11,12,13])
    p_g = np.array([
        [20,21,22],
        [0,0,0],
        [30,31,32],
    ])

    expected = np.array([
        [31,33,35],
        [110,218,326],
        [140,249,358],
    ])

    actual = project._calc_mirror(R_ar, s_gm, p_g)

    nptest.assert_allclose(actual, expected, rtol=0, atol=1e-7)

def test_calc_incidence():
    R_ar = np.array([
        [[1,0,0],
         [0,1,0],
         [0,0,1]],
        [[2,3,4],
         [5,6,7],
         [8,9,10]],
    ])
    t_la_z = 10.
    t_la_x = 20.

    expected = np.array([
        [0.1631759112,-0.9254165784,-0.3420201433],
        [-3.817978486,-7.130760918,-10.44354335],
    ])

    actual = project._calc_incidence(R_ar, t_la_z, t_la_x)

    nptest.assert_allclose(actual, expected, rtol=0, atol=1e-7)

def test_calc_normal():
    R_ar = np.array([
        [[1,0,0],
         [0,1,0],
         [0,0,1]],
        [[2,3,4],
         [5,6,7],
         [8,9,10]],
    ])
    t_ma_z = 10.
    t_ma_x = 20.
    t_ma_y = 30.

    expected = np.array([
        [0.5438381425,-0.2048741287,0.8137976813],
        [3.728244624,7.18652971,10.6448148],
    ])

    actual = project._calc_normal(R_ar, t_ma_z, t_ma_x, t_ma_y)

    nptest.assert_allclose(actual, expected, rtol=0, atol=1e-7)

def test_calc_reflection():
    dv_i = np.array([
        [0,0,1],
        [0,0,1],
        [0,1,0],
        [0,1,0],
        [1,0,0],
        [1,0,0],
        [1,2,3],
    ])
    dv_n = np.array([
        [0,1,0],
        [1,0,0],
        [0,0,1],
        [1,0,0],
        [0,0,1],
        [0,1,0],
        [4,5,6],
    ])

    expected = np.array([
        [0,0,-1],
        [0,0,-1],
        [0,-1,0],
        [0,-1,0],
        [-1,0,0],
        [-1,0,0],
        [255,318,381],
    ])

    actual = project._calc_reflection(dv_i, dv_n)

    nptest.assert_allclose(actual, expected, rtol=0, atol=1e-7)

def test_calc_target():
    dv_s = np.array([
        [0,0,1],
        [0,1,0],
        [1,0,0],
        [3,4,5],
    ])
    r_mt = np.array([100,200,300,500])
    p_m = np.array([
        [1,2,3],
        [4,5,6],
        [7,8,9],
        [10,20,30],
    ])

    expected = np.array([
        [1,2,103],
        [4,205,6],
        [307,8,9],
        [1510,2020,2530],
    ])

    actual = project._calc_target(dv_s, r_mt, p_m)

    nptest.assert_allclose(actual, expected, rtol=0, atol=1e-7)
