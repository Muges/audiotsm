# -*- coding: utf-8 -*-

"""
audiotsm.io.base
~~~~~~~~~~~~~~~~

This module provides base classes for the input and output of the TSM objects.
"""


class Reader(object):
    """An abstract class for the input of a TSM object."""

    @property
    def channels(self):
        """The number of channels of the Reader."""
        raise NotImplementedError()

    def read(self, buffer):
        """Reads as many samples from the Reader as possible, write them to
        ``buffer``, and returns the number of samples that were read.

        :param buffer: a matrix of size (m, n), with m the number of channels
            and n the length of the buffer, where the samples will be written.
        :type buffer: :class:`numpy.ndarray`
        :returns: the number of samples that were read. It will always be equal
            to the length of the buffer, except when there is no more values to
            be read.
        :raises ValueError: if the Reader and the buffer do not have the same
            number of channels
        """
        raise NotImplementedError()


class Writer(object):
    """An abstract class for the output of a TSM object."""

    @property
    def channels(self):
        """The number of channels of the Writer."""
        raise NotImplementedError()

    def write(self, buffer):
        """Write as many samples from the Writer as possible from ``buffer``,
        and returns the number of samples that were written.

        :param buffer: a matrix of size (m, n), with m the number of channels
            and n the length of the buffer, where the samples will be written.
        :type buffer: :class:`numpy.ndarray`
        :returns: the number of samples that were written. It will always be
            equal to the length of the buffer, except when there is no more
            space in the Writer.
        :raises ValueError: if the Writer and the buffer do not have the same
            number of channels
        """
        raise NotImplementedError()
