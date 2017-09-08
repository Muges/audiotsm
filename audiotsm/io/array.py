# -*- coding: utf-8 -*-

"""
audiotsm.io.array
~~~~~~~~~~~~~~~~~

This module provides a Reader and a Writer allowing to use
:class:`numpy.ndarray` as input and output of a TSM object.
"""

import numpy as np

from . import base


class ArrayReader(base.Reader):
    """A Reader allowing to use :class:`numpy.ndarray` as input of a TSM
    object.

    :param data: a matrix of size (m, n), with m the number of channels and n
        the length of the buffer, where the samples will be written.
    :type data: :class:`numpy.ndarray`
    """
    def __init__(self, data):
        self._data = data

    @property
    def channels(self):
        return self._data.shape[0]

    @property
    def empty(self):
        return self._data.shape[1] == 0

    def read(self, buffer):
        if buffer.shape[0] != self._data.shape[0]:
            raise ValueError("the two buffers should have the same number of "
                             "channels")

        # Number of samples to read
        n = min(buffer.shape[1], self._data.shape[1])
        np.copyto(buffer[:, :n], self._data[:, :n])

        # Remove the samples that were read
        self._data = self._data[:, n:]

        return n

    def skip(self, n):
        if n > self._data.shape[1]:
            n = self._data.shape[1]

        self._data = self._data[:, n:]

        return n


class ArrayWriter(base.Writer):
    """A Writer allowing to use :class:`numpy.ndarray` as output of a TSM
    object.

    :param data: a matrix of size (m, n), with m the number of channels and n
        the length of the buffer, where the samples will be written.
    :type data: :class:`numpy.ndarray`
    """
    def __init__(self, data):
        self._data = data

    @property
    def channels(self):
        return self._data.shape[0]

    def write(self, buffer):
        if buffer.shape[0] != self._data.shape[0]:
            raise ValueError("the two buffers should have the same number of "
                             "channels")

        # Number of samples to write
        n = min(buffer.shape[1], self._data.shape[1])
        np.copyto(self._data[:, :n], buffer[:, :n])

        self._data = self._data[:, n:]

        return n
