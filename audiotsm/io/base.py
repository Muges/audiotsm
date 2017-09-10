# -*- coding: utf-8 -*-

"""
The :mod:`audiotsm.io.base` module provides base classes for the input and
output of :class:`~audiotsm.base.tsm.TSM` objects.
"""


class Reader(object):
    """An abstract class for the input of a :class:`~audiotsm.base.tsm.TSM`
    object."""

    @property
    def channels(self):
        """The number of channels of the :class:`~audiotsm.io.base.Reader`."""
        raise NotImplementedError()

    @property
    def empty(self):
        """True if there is no more data to read."""
        raise NotImplementedError()

    def read(self, buffer):
        """Reads as many samples from the :class:`~audiotsm.io.base.Reader` as
        possible, write them to ``buffer``, and returns the number of samples
        that were read.

        :param buffer: a matrix of shape (``m``, ``n``), with ``m`` the number
            of channels and ``n`` the length of the buffer, where the samples
            will be written.
        :type buffer: :class:`numpy.ndarray`
        :returns: the number of samples that were read. It should always be
            equal to the length of the buffer, except when there is no more
            values to be read.
        :raises ValueError: if the :class:`~audiotsm.io.base.Reader` and the
            buffer do not have the same number of channels
        """
        raise NotImplementedError()

    def skip(self, n):
        """Try to skip ``n`` samples, an returns the number of samples that
        were actually skipped."""
        raise NotImplementedError()


class Writer(object):
    """An abstract class for the output of a :class:`~audiotsm.base.tsm.TSM`
    object."""

    @property
    def channels(self):
        """The number of channels of the :class:`~audiotsm.io.base.Writer`."""
        raise NotImplementedError()

    def write(self, buffer):
        """Write as many samples from the :class:`~audiotsm.io.base.Writer` as
        possible from ``buffer``, and returns the number of samples that were
        written.

        :param buffer: a matrix of shape (``m``, ``n``), with ``m`` the number
            of channels and ``n`` the length of the buffer, where the samples
            will be read.
        :type buffer: :class:`numpy.ndarray`
        :returns: the number of samples that were written. It should always be
            equal to the length of the buffer, except when there is no more
            space in the :class:`~audiotsm.io.base.Writer`.
        :raises ValueError: if the :class:`~audiotsm.io.base.Writer` and the
            buffer do not have the same number of channels
        """
        raise NotImplementedError()
