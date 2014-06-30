import numpy as np
from scipy.signal import hilbert

from obspy.noise.header import clibnoise


def phase_xcorr(data1, data2, max_lag, nu=1, min_lag=0):
    """
    # Phase cross correlation (Schimmel 1999); this is obtained with a
    variable # window length

    data1, data2: Numpy arrays containing the analytic signal normalized
    sample by sample
    by their absolute value (ie containing only the instantaneous phase
    information)
    max_lag: maximum lag in number of samples, integer
    """
    #Initialize pcc array:
    pxc = np.zeros((2 * max_lag + 1,), dtype=np.float64)

    #Obtain analytic signal
    data1 = hilbert(data1)
    data2 = hilbert(data2)

    #Normalization
    data1 = data1 / (np.abs(data1))
    data2 = data2 / (np.abs(data2))

    clibnoise.phase_xcorr_loop(data1, data2, len(data1), pxc, float(nu),
                               int(max_lag), int(min_lag))

    if min_lag:
        pxc = np.ma.array(pxc)
        pxc[-min_lag: min_lag] = True

    # for k in range(0, max_lag + 1):
    #     i11 = 0
    #     i12 = len(data1) - k
    #     i21 = k
    #     i22 = len(data1)
    #
    #     pxc[max_lag + k] = 1.0 / float(2.0 * len(data1) - k) * \
    #         (np.sum(np.abs(data1[i11:i12] +
    #                        data2[i21:i22]) ** nu) -
    #          np.sum(np.abs(data1[i11:i12] -
    #                        data2[i21:i22]) ** nu))
    #     pxc[max_lag - k] = 1.0 / float(2.0 * len(data1) - k) * \
    #         (np.sum(np.abs(data1[i21:i22] +
    #                        data2[i11:i12]) ** nu) -
    #          np.sum(np.abs(data1[i21:i22] -
    #                        data2[i11:i12]) ** nu))

    return pxc