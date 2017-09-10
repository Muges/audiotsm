# -*- coding: utf-8 -*-

"""
The :mod:`audiotsm.io.array` module provides a Reader and Writers allowing to
use a :class:`numpy.ndarray` as input or output of a
:class:`~audiotsm.base.tsm.TSM` object.
"""

import numpy as np

from . import base


class ArrayReader(base.Reader):
    """A :class:`~audiotsm.io.base.Reader` allowing to use
    :class:`numpy.ndarray` as input of a :class:`~audiotsm.base.tsm.TSM`
    object.

    :param data: a matrix of shape (``m``, ``n``), with ``m`` the number of
        channels and ``n`` the length of the buffer, where the samples will be
        read.
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
    """A :class:`~audiotsm.io.base.Writer` allowing to get the output of a
    :class:`~audiotsm.base.tsm.TSM` object as a :class:`numpy.ndarray`.

    Writing to an :class:`~audiotsm.io.array.ArrayWriter` will add the data at
    the end of the :attr:`~audiotsm.io.array.ArrayWriter.data` attribute.

    :param channels: the number of channels of the signal.
    :type channels: int
    """

    def __init__(self, channels):
        self._channels = channels
        self._data = []

    @property
    def channels(self):
        return self._channels

    def write(self, buffer):
        if buffer.shape[0] != self._channels:
            raise ValueError("the buffer should have the same number of "
                             "channels as the ArrayWriter")

        self._data.append(np.copy(buffer))

        return buffer.shape[1]

    @property
    def data(self):
        """A :class:`numpy.ndarray` of shape (``m``, ``n``), with ``m`` the
        number of channels and ``n`` the length of the data, where the samples
        have written."""
        if not self._data:
            return np.ndarray((self._channels, 0), dtype=np.float32)

        data = np.concatenate(self._data, axis=1)
        self._data = [data]

        return data


class FixedArrayWriter(base.Writer):
    """A :class:`~audiotsm.io.base.Writer` allowing to use
    :class:`numpy.ndarray` as output of a TSM object.

    Contrary to an :class:`~audiotsm.io.array.ArrayWriter`, a
    :class:`~audiotsm.io.array.FixedArrayWriter` takes the buffer in which the
    data will be written as a parameter of its constructor. The buffer is of
    fixed size, and it will not be possible to write more samples to the
    :class:`~audiotsm.io.array.FixedArrayWriter` than the buffer can contain.

    :param data: a matrix of shape (``m``, ``n``), with ``m`` the number of
        channels and ``n`` the length of the buffer, where the samples will be
        written.
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
