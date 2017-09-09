# -*- coding: utf-8 -*-

"""
audiotsm.base
~~~~~~~~~~~~~

This module provides a base classes for real-time audio time-scale modification
procedures.
"""

from audiotsm.io.array import ArrayReader, FixedArrayWriter


class TSM(object):
    """An abstract class for real-time audio time-scale modification
    procedures.

    The buffers used in arguments of the :func:`TSM.flush`, :func:`TSM.put` and
    :func:`TSM.receive` methods should be matrices of shape (m, n), where m is
    the number of channels, and n is the number of samples per channels. For
    example, if a ``buffer`` contains a stereo signal, it should be a matrix
    with two rows, ``buffer[0][i]`` should be the i-th sample of the left
    channel, and ``buffer[1][i]`` the i-th sample of the right channel.
    """

    def clear(self):
        """Clears the state of the TSM object, making it ready to be used on
        another signal (or another part of a signal)."""
        raise NotImplementedError

    def flush(self, buffer):
        """Writes the last output samples to the buffer, assuming that no
        samples will be added to the input, and returns the number of samples
        that were written.

        :param buffer: a matrix of size (m, n), with m the number of channels
            and n the length of the buffer, where the samples will be written.
        :type buffer: :class:`numpy.ndarray`
        :returns: the number of samples that were written. It will always be
            equal to the length of the buffer, except when there is no more
            values to be written.
        """
        return self.flush_to(FixedArrayWriter(buffer))

    def flush_to(self, writer):
        """Writes as many output samples as possible to ``writer``, assuming
        that no samples will be added to the input, and returns the number of
        samples that were written.

        :param writer: a :class:`audiotsm.io.Writer`
        :returns: the number of samples that were written to ``writer``, and a
            boolean that is True if there are no samples remaining to flush.
        :rtype: (int, bool)
        """
        raise NotImplementedError

    def put(self, buffer):
        """Reads samples from ``buffer`` and processes them. It returns the
        number of samples that were read.

        :param buffer: a matrix of size (m, n), with m the number of channels
            and n the length of the buffer, where the samples will be read.
        :type buffer: :class:`numpy.ndarray`
        :returns: the number of samples that were read from the buffer. If it
            is lower than the length of the buffer, some of the samples were
            not read. You can use the :func:`TSM.remaining_input_space` method
            to know in advance how many samples can be processed.
        """
        return self.read_from(ArrayReader(buffer))

    def read_from(self, reader):
        """Reads as many samples as possible from ``reader``, processes them,
        and returns the number of samples that were read.

        :param reader: a :class:`audiotsm.io.Reader`
        :returns: the number of samples that were read from ``reader``.
        """
        raise NotImplementedError

    def receive(self, buffer):
        """Writes the result of the time-scale modification procedure to
        ``buffer``, and returns the number of samples that were written.

        :param buffer: a matrix of size (m, n), with m the number of channels
            and n the length of the buffer, where the samples will be written.
        :type buffer: :class:`numpy.ndarray`
        :returns: the number of samples that were written. It will always be
            equal to the length of the buffer, except when there is no more
            values to be written. In this case, you should either call
            :func:`TSM.put` to provide more input samples, or :func:`TSM.flush`
            if there is no input samples remaining.
        """
        return self.write_to(FixedArrayWriter(buffer))[0]

    def remaining_input_space(self):
        """Return the number of samples that can be processed by the
        :func:`TSM.put` method."""
        raise NotImplementedError

    def run(self, reader, writer):
        """Run the TSM procedure on the content of ``reader`` and write the
        output to ``writer``.

        :param reader: a :class:`audiotsm.io.Reader`
        :param writer: a :class:`audiotsm.io.Writer`
        """
        finished = False
        while not (finished and reader.empty):
            self.read_from(reader)
            _, finished = self.write_to(writer)

        finished = False
        while not finished:
            _, finished = self.flush_to(writer)

    def set_speed(self, speed):
        """Set the speed ratio."""
        raise NotImplementedError

    def write_to(self, writer):
        """Writes as many result samples as possible to ``writer``, and returns
        the number of samples that were written.

        :param writer: a :class:`audiotsm.io.Writer`
        :returns: the number of samples that were written to ``writer``, and a
            boolean that is True if there are no samples remaining to write.
        """
        raise NotImplementedError
