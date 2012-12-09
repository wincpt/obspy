#!/usr/bin/env python

from obspy import Trace, Stream, UTCDateTime
from obspy.core.util import AttribDict
from obspy.signal.array_analysis import array_transff_freqslowness, \
  array_processing
from obspy.signal.array_analysis import array_transff_wavenumber
from obspy.signal.util import utlLonLat
import numpy as np
import unittest
from cStringIO import StringIO


class SonicTestCase(unittest.TestCase):
    """
    Test fk analysis, main function is sonic() in array_analysis.py
    """

    def arrayProcessing(self, prewhiten, method):
        np.random.seed(2348)

        geometry = np.array([[0.0, 0.0, 0.0],
                             [-5.0, 7.0, 0.0],
                             [5.0, 7.0, 0.0],
                             [10.0, 0.0, 0.0],
                             [5.0, -7.0, 0.0],
                             [-5.0, -7.0, 0.0],
                             [-10.0, 0.0, 0.0]])

        geometry /= 100      # in km
        slowness = 1.3       # in s/km
        baz_degree = 20.0    # 0.0 > source in x direction
        baz = baz_degree * np.pi / 180.
        df = 100             # samplerate
        # SNR = 100.         # signal to noise ratio
        amp = .00001         # amplitude of coherent wave
        length = 500         # signal length in samples

        coherent_wave = amp * np.random.randn(length)

        # time offsets in samples
        dt = df * slowness * (np.cos(baz) * geometry[:, 1] + np.sin(baz) *
                              geometry[:, 0])
        dt = np.round(dt)
        dt = dt.astype('int32')
        max_dt = np.max(dt) + 1
        min_dt = np.min(dt) - 1
        trl = list()
        for i in xrange(len(geometry)):
            tr = Trace(coherent_wave[-min_dt + dt[i]:-max_dt + dt[i]].copy())
                # + amp / SNR * \
                # np.random.randn(length - abs(min_dt) - abs(max_dt)))
            tr.stats.sampling_rate = df
            tr.stats.coordinates = AttribDict()
            tr.stats.coordinates.x = geometry[i, 0]
            tr.stats.coordinates.y = geometry[i, 1]
            tr.stats.coordinates.elevation = geometry[i, 2]
            # lowpass random signal to f_nyquist / 2
            tr.filter("lowpass", freq=df / 4.)
            trl.append(tr)

        st = Stream(trl)

        stime = UTCDateTime(1970, 1, 1, 0, 0)
        etime = UTCDateTime(1970, 1, 1, 0, 0) + \
                (length - abs(min_dt) - abs(max_dt)) / df

        win_len = 2.
        step_frac = 0.2
        sll_x = -3.0
        slm_x = 3.0
        sll_y = -3.0
        slm_y = 3.0
        sl_s = 0.1

        frqlow = 1.0
        frqhigh = 8.0

        semb_thres = -1e99
        vel_thres = -1e99

        args = (st, win_len, step_frac, sll_x, slm_x, sll_y, slm_y, sl_s,
                semb_thres, vel_thres, frqlow, frqhigh, stime, etime)
        kwargs = dict(prewhiten=prewhiten, coordsys='xy', verbose=False,
                      method=method)
        out = array_processing(*args, **kwargs)
        if 0:  # 1 for debugging
            print '\n', out[:, 1:]
        return out

    def test_sonicBf(self):
        out = self.arrayProcessing(prewhiten=0, method=0)
        raw = """
9.69515476e-01 1.95237117e-05 1.84349488e+01 1.26491106e+00
9.59920378e-01 1.68637467e-05 1.84349488e+01 1.26491106e+00
9.63367672e-01 1.36251275e-05 1.84349488e+01 1.26491106e+00
9.65265591e-01 1.35077292e-05 1.84349488e+01 1.26491106e+00
9.56276421e-01 1.15114010e-05 1.84349488e+01 1.26491106e+00
9.49731735e-01 9.66531018e-06 1.84349488e+01 1.26491106e+00
        """
        ref = np.loadtxt(StringIO(raw), dtype='f4')
        np.testing.assert_allclose(ref, out[:, 1:], rtol=1e-6)

    def test_sonicBfPrew(self):
        out = self.arrayProcessing(prewhiten=1, method=0)
        raw = """
1.41116437e-01 1.95237117e-05 1.84349488e+01 1.26491106e+00
1.28633209e-01 1.68637467e-05 1.84349488e+01 1.26491106e+00
1.30422122e-01 1.36251275e-05 1.84349488e+01 1.26491106e+00
1.33438392e-01 1.35077292e-05 1.84349488e+01 1.26491106e+00
1.32708065e-01 1.15114010e-05 1.84349488e+01 1.26491106e+00
1.31982873e-01 9.66531018e-06 1.84349488e+01 1.26491106e+00
        """
        ref = np.loadtxt(StringIO(raw), dtype='f4')
        np.testing.assert_allclose(ref, out[:, 1:])

    def test_sonicCapon(self):
        out = self.arrayProcessing(prewhiten=0, method=1)
        raw = """
8.57600009e-01 8.57600009e-01  1.49314172e+01 1.55241747e+00
1.72793618e+04 1.72793618e+04 -1.48240520e+02 2.46981781e+00
4.58603016e+02 4.58603016e+02  1.54653824e+02 2.10237960e+00
7.28814121e+02 7.28814121e+02  1.58198591e+02 1.07703296e+00
9.43803974e+02 9.43803974e+02 -9.78533133e+01 2.92745623e+00
2.04031354e+02 2.04031354e+02 -7.50685828e+01 1.55241747e+00
        """
        ref = np.loadtxt(StringIO(raw), dtype='f4')
        # XXX relative tolerance should be lower!
        np.testing.assert_allclose(ref, out[:, 1:], rtol=5e-3)

    def test_sonicCaponPrew(self):
        out = self.arrayProcessing(prewhiten=1, method=1)
        raw = """
1.28958194e-01 8.57600009e-01 1.49314172e+01 1.55241747e+00
8.67841733e-03 2.46878767e+00 6.11550357e+00 2.81602557e+00
1.62662506e-02 1.01472317e+02 3.55376778e+01 8.60232527e-01
1.16868438e-02 2.58679345e+01 2.65650512e+01 8.94427191e-01
1.78311467e-02 3.35905434e+01 1.97988764e+01 2.65706605e+00
2.39100818e-02 1.87168023e+02 1.68690068e+02 1.52970585e+00
        """
        ref = np.loadtxt(StringIO(raw), dtype='f4')
        # XXX relative tolerance should be lower!
        np.testing.assert_allclose(ref, out[:, 1:], rtol=4e-5)

    def test_array_transff_freqslowness(self):

        coords = np.array([[10., 60., 0.],
                           [200., 50., 0.],
                           [-120., 170., 0.],
                           [-100., -150., 0.],
                           [30., -220., 0.]])

        coords /= 1000.

        coordsll = np.zeros(coords.shape)
        for i in np.arange(len(coords)):
            coordsll[i, 0], coordsll[i, 1] = utlLonLat(0., 0., coords[i, 0],
                                                       coords[i, 1])

        slim = 40.
        fmin = 1.
        fmax = 10.
        fstep = 1.

        sstep = slim / 2.

        transff = array_transff_freqslowness(coords, slim, sstep, fmin, fmax,
                fstep, coordsys='xy')

        transffll = array_transff_freqslowness(coordsll, slim, sstep, fmin,
                fmax, fstep, coordsys='lonlat')

        transffth = np.array(
            [[0.41915119, 0.33333333, 0.32339525, 0.24751548, 0.67660475],
             [0.25248452, 0.41418215, 0.34327141, 0.65672859, 0.33333333],
             [0.24751548, 0.25248452, 1.00000000, 0.25248452, 0.24751548],
             [0.33333333, 0.65672859, 0.34327141, 0.41418215, 0.25248452],
             [0.67660475, 0.24751548, 0.32339525, 0.33333333, 0.41915119]])

        np.testing.assert_array_almost_equal(transff, transffth, decimal=6)
        np.testing.assert_array_almost_equal(transffll, transffth, decimal=6)

    def test_array_transff_wavenumber(self):

        coords = np.array([[10., 60., 0.],
                           [200., 50., 0.],
                           [-120., 170., 0.],
                           [-100., -150., 0.],
                           [30., -220., 0.]])

        coords /= 1000.

        coordsll = np.zeros(coords.shape)
        for i in np.arange(len(coords)):
            coordsll[i, 0], coordsll[i, 1] = utlLonLat(0., 0., coords[i, 0],
                                                       coords[i, 1])

        klim = 40.
        kstep = klim / 2.

        transff = array_transff_wavenumber(coords, klim, kstep, coordsys='xy')
        transffll = array_transff_wavenumber(coordsll, klim, kstep,
                                             coordsys='lonlat')

        transffth = np.array(
            [[3.13360360e-01, 4.23775796e-02, 6.73650243e-01,
              4.80470652e-01, 8.16891615e-04],
             [2.98941684e-01, 2.47377842e-01, 9.96352135e-02,
              6.84732871e-02, 5.57078203e-01],
             [1.26523678e-01, 2.91010683e-01, 1.00000000e+00,
              2.91010683e-01, 1.26523678e-01],
             [5.57078203e-01, 6.84732871e-02, 9.96352135e-02,
              2.47377842e-01, 2.98941684e-01],
             [8.16891615e-04, 4.80470652e-01, 6.73650243e-01,
              4.23775796e-02, 3.13360360e-01]])

        np.testing.assert_array_almost_equal(transff, transffth, decimal=6)
        np.testing.assert_array_almost_equal(transffll, transffth, decimal=6)


def suite():
    return unittest.makeSuite(SonicTestCase, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')