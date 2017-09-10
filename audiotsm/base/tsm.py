# -*- coding: utf-8 -*-

"""
The :mod:`audiotsm.base.tsm` module provides a base class for real-time audio
time-scale modification procedures.
"""


class TSM(object):
    """An abstract class for real-time audio time-scale modification
    procedures."""

    def clear(self):
        """Clears the state of the TSM object, making it ready to be used on
        another signal (or another part of a signal)."""
        raise NotImplementedError

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

    def read_from(self, reader):
        """Reads as many samples as possible from ``reader``, processes them,
        and returns the number of samples that were read.

        :param reader: a :class:`audiotsm.io.Reader`
        :returns: the number of samples that were read from ``reader``.
        """
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
