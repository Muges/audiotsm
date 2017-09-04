# -*- coding: utf-8 -*-

"""
audiotsm.windows
~~~~~~~~~~~~~~~~

This module contains window functions used for digital signal processing.
"""

import numpy as np


def hanning(length):
    """Returns a periodic Hanning window.

    Contrary to :func:`numpy.hanning`, which returns the symetric Hanning
    window, :func:`hanning` returns a periodic Hanning window, which is better
    for spectral analysis.

    :param length: the number of points of the Hanning window
    :type length: :class:`int`
    :return: the window as a :class:`numpy.ndarray`
    """
    if length <= 0:
        return np.zeros(0)

    time = np.arange(length)
    return 0.5 * (1 - np.cos(2 * np.pi * time / length))
