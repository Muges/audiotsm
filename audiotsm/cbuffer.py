# -*- coding: utf-8 -*-

"""
audiotsm.cbuffer
~~~~~~~~~~~~~~~~

This module implements a circular buffer used to store multichannel audio data.
"""

import numpy as np


class CBuffer(object):
    """A CBuffer is a circular buffer used to store multichannel audio data.

    It can be seen as a variable-size buffer whose length is bounded by
    max_length. The :func:`CBuffer.write` and :func:`CBuffer.right_pad`
    methods allow to add samples at the end of the buffer, while the
    :func:`CBuffer.read` and :func:`CBuffer.remove` methods allow to remove
    samples from the beginning of the buffer.

    :param channels: the number of channels of the buffer.
    :type channels: int
    :param max_length: the maximum length of the buffer (i.e. the maximum
        number of samples that can be stored in each channel)
    :type max_length: int
    """
    def __init__(self, channels, max_length):
        self._data = np.zeros((channels, max_length), dtype=np.float32)
        self._channels = channels
        self._max_length = max_length

        self._offset = 0
        self._length = 0

    def __repr__(self):
        return "CBuffer(offset={}, length={}, data=\n{})".format(
            self._offset, self._length, repr(self.to_array()))

    def add(self, buffer):
        """Adds a buffer element-wise to the CBuffer.

        :param buffer: a matrix of size (m, n), with m the number of channels
            and n the length of the buffer.
        :type buffer: :class:`numpy.ndarray`
        :raises ValueError: if the CBuffer and the buffer do not have the same
            number of channels or there is not enough space to add the zeros.
        """
        if buffer.shape[0] != self._data.shape[0]:
            raise ValueError("the two buffers should have the same number of "
                             "channels")

        n = buffer.shape[1]
        if n > self._length:
            raise ValueError("not enough space remaining in CBuffer")

        # Compute the slice of data where the values will be added
        start = self._offset
        end = self._offset + n

        if end <= self._max_length:
            self._data[:, start:end] += buffer[:, :n]
        else:
            end -= self._max_length
            self._data[:, start:] += buffer[:, :self._max_length - start]
            self._data[:, :end] += buffer[:, self._max_length - start:n]

    def divide(self, array):
        """Divides each channel of the CBuffer element-wise by the array.

        :type array: An array of dimension one.
        :type array: :class:`numpy.ndarray`
        :raises ValueError: if there is not enough space in the CBuffer.
        """
        n = len(array)
        if n > self._length:
            raise ValueError("not enough space remaining in the CBuffer")

        # Compute the slice of data where the values will be divided
        start = self._offset
        end = self._offset + n

        if end <= self._max_length:
            self._data[:, start:end] /= array[:n]
        else:
            end -= self._max_length
            self._data[:, start:] /= array[:self._max_length - start]
            self._data[:, :end] /= array[self._max_length - start:n]

    def length(self):
        """Returns the length of the CBuffer."""
        return self._length

    def peek(self, buffer):
        """Reads as many samples from the CBuffer as possible, without removing
        them from the CBuffer, writes them to the buffer, and returns the
        number of samples that were read.

        :param buffer: a matrix of size (m, n), with m the number of channels
            and n the length of the buffer, where the samples will be written.
        :type buffer: :class:`numpy.ndarray`
        :returns: the number of samples that were read from the CBuffer.
        :raises ValueError: if the CBuffer and the buffer do not have the same
            number of channels
        """
        if buffer.shape[0] != self._data.shape[0]:
            raise ValueError("the two buffers should have the same number of "
                             "channels")

        n = min(buffer.shape[1], self._length)

        # Compute the slice of data where the values will be added
        start = self._offset
        end = self._offset + n

        if end <= self._max_length:
            np.copyto(buffer[:, :n], self._data[:, start:end])
        else:
            end -= self._max_length
            np.copyto(buffer[:, :self._max_length - start],
                      self._data[:, start:])
            np.copyto(buffer[:, self._max_length - start:n],
                      self._data[:, :end])

        return n

    def read(self, buffer):
        """Reads as many samples from the CBuffer as possible, removes them
        from the CBuffer, writes them to the buffer, and returns the number of
        samples that were read.

        :param buffer: a matrix of size (m, n), with m the number of channels
            and n the length of the buffer, where the samples will be written.
        :type buffer: :class:`numpy.ndarray`
        :returns: the number of samples that were read from the CBuffer.
        :raises ValueError: if the CBuffer and the buffer do not have the same
            number of channels
        """
        n = self.peek(buffer)
        self.remove(n)
        return n

    def remaining_length(self):
        """Returns the number of samples that can be added to the CBuffer."""
        return self._max_length - self._length

    def remove(self, n):
        """Removes the first n samples of the CBuffer, preventing them to be
        read again, and leaving more space for new samples to be written.

        :param n: the number of samples to remove.
        :type n: int
        """
        if n >= self._length:
            n = self._length

        # Compute the slice of data that will be reset to 0
        start = self._offset
        end = self._offset + n

        if end <= self._max_length:
            self._data[:, start:end] = 0
        else:
            end -= self._max_length
            self._data[:, start:] = 0
            self._data[:, :end] = 0

        self._offset += n
        self._offset %= self._max_length
        self._length -= n

    def right_pad(self, n):
        """Add zeros to the right of the CBuffer.

        :param n: the number of zeros to add.
        :type n: int
        :raises ValueError: if there is not enough space to add the zeros.
        """
        if n > self._max_length - self._length:
            raise ValueError("not enough space remaining in CBuffer")

        self._length += n

    def to_array(self):
        """Returns an array containing the same data as the CBuffer.

        :returns: :class:`numpy.ndarray`
        """
        out = np.empty((self._channels, self._length))
        self.peek(out)
        return out

    def write(self, buffer):
        """Writes as many samples to the CBuffer as possible, and returns the
        number of samples that were read.

        :param buffer: a matrix of size (m, n), with m the number of channels
            and n the length of the buffer, where the samples will be read.
        :type buffer: :class:`numpy.ndarray`
        :returns: the number of samples that were written to the CBuffer.
        :raises ValueError: if the CBuffer and the buffer do not have the same
            number of channels
        """
        if buffer.shape[0] != self._data.shape[0]:
            raise ValueError("the two buffers should have the same number of "
                             "channels")

        n = min(buffer.shape[1], self._max_length - self._length)

        # Compute the slice of data that will be written to
        start = (self._offset + self._length) % self._max_length
        end = start + n

        if end <= self._max_length:
            np.copyto(self._data[:, start:end], buffer[:, :n])
        else:
            # There is not enough space to copy the whole buffer, it has to be
            # split into two parts, one of which will be copied at the end of
            # _data, and the other at the beginning.
            end -= self._max_length

            np.copyto(self._data[:, start:],
                      buffer[:, :self._max_length - start])
            np.copyto(self._data[:, :end],
                      buffer[:, self._max_length - start:n])

        self._length += n
        return n


class NormalizeBuffer(object):
    """A NormalizeBuffer is a mono-channel circular buffer, used to normalize
    audio buffers.

    :param length: the length of the NormalizeBuffer.
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
        """Adds a window element-wise to the NormalizeBuffer.

        :param window: an array of dimension 1.
        :type window: :class:`numpy.ndarray`
        :raises ValueError: if the window is larger than the buffer.
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

    def remove(self, n):
        """Removes the first n values of the NormalizeBuffer.

        :param n: the number of samples to remove.
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
        NormalizeBuffer[start:end].

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
