# -*- coding: utf-8 -*-

"""
audiotsm.utils.windows
~~~~~~~~~~~~~~~~~~~~~~

This module contains window functions used for digital signal processing.
"""

import numpy as np


def apply(buffer, window):
    """Applies a window to a buffer.

    :param buffer: a matrix of size (m, n), with m the number of channels and
        n the length of the buffer, where the samples will be written.
    :type buffer: :class:`numpy.ndarray`
    :param window: a :class:`numpy.ndarray` of shape (n,).
    """
    if window is None:
        return

    for channel in buffer:
        channel *= window


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


def product(window1, window2):
    """Returns the product of two windows."""
    if window1 is None:
        return window2

    if window2 is None:
        return window1

    return window1 * window2
