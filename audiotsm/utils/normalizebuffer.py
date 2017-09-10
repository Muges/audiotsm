# -*- coding: utf-8 -*-

"""
The :mod:`audiotsm.normalizebuffer` module implements a mono-channel circular
buffer used to normalize audio buffers.
"""

import numpy as np


class NormalizeBuffer(object):
    """A :class:`NormalizeBuffer` is a mono-channel circular buffer, used to
    normalize audio buffers.

    :param length: the length of the :class:`NormalizeBuffer`.
    :type length: int
    """
    def __init__(self, length):
        self._data = np.zeros(length)
        self._offset = 0
        self._length = length

    def __repr__(self):
        return "NormalizeBuffer(offset={}, length={}, data=\n{})".format(
            self._offset, self._length, repr(self.to_array()))

    def add(self, window):
        """Adds a window element-wise to the :class:`NormalizeBuffer`.

        :param window: an array of shape (``n``,).
        :type window: :class:`numpy.ndarray`
        :raises ValueError: if the window is larger than the buffer (``n >
            self.length``).
        """
        n = len(window)
        if n > self._length:
            raise ValueError("the window should be smaller than the "
                             "NormalizeBuffer")

        # Compute the slice of data where the values will be added
        start = self._offset
        end = self._offset + n

        if end <= self._length:
            self._data[start:end] += window
        else:
            end -= self._length
            self._data[start:] += window[:self._length - start]
            self._data[:end] += window[self._length - start:]

    @property
    def length(self):
        """The length of the CBuffer."""
        return self._length

    def remove(self, n):
        """Removes the first ``n`` values of the :class:`NormalizeBuffer`.

        :param n: the number of values to remove.
        :type n: int
        """
        if n >= self._length:
            n = self._length
        if n == 0:
            return

        # Compute the slice of data to reset
        start = self._offset
        end = self._offset + n

        if end <= self._length:
            self._data[start:end] = 0
        else:
            end -= self._length
            self._data[start:] = 0
            self._data[:end] = 0

        self._offset += n
        self._offset %= self._length

    def to_array(self, start=0, end=None):
        """Returns an array containing the same data as the
        :class:`NormalizeBuffer`, from index ``start`` (included) to index
        ``end`` (exluded).

        :returns: :class:`numpy.ndarray`
        """
        if end is None:
            end = self._length

        start += self._offset
        end += self._offset

        if end <= self._length:
            return np.copy(self._data[start:end])

        end -= self._length
        if start < self._length:
            return np.concatenate((self._data[start:], self._data[:end]))

        start -= self._length
        return np.copy(self._data[start:end])
