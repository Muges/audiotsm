# -*- coding: utf-8 -*-

"""
The :mod:`audiotsm.base.tsm` module provides an abstract class for real-time
audio time-scale modification procedures.
"""


class TSM(object):
    """An abstract class for real-time audio time-scale modification
    procedures.

    If you want to use a :class:`~audiotsm.base.tsm.TSM` object to run a TSM
    procedure on a signal, you should use the
    :func:`~audiotsm.base.tsm.TSM.run` method in most cases.
    """

    def clear(self):
        """Clears the state of the :class:`~audiotsm.base.tsm.TSM` object,
        making it ready to be used on another signal (or another part of a
        signal).

        This method should be called before processing a new file, or seeking
        to another part of a signal.
        """
        raise NotImplementedError

    def flush_to(self, writer):
        """Writes as many output samples as possible to ``writer``, assuming
        that there are no remaining samples that will be added to the input
        (i.e. that the :func:`~audiotsm.base.tsm.TSM.write_to` method will not
        be called), and returns the number of samples that were written.

        :param writer: a :class:`audiotsm.io.base.Writer`.
        :returns: a tuple (``n``, ``finished``), with:

            - ``n`` the number of samples that were written to ``writer``
            - ``finished`` a boolean that is ``True`` when there are no samples
              remaining to flush.
        :rtype: (int, bool)
        """
        raise NotImplementedError

    def get_max_output_length(self, input_length):
        """Returns the maximum number of samples that will be written to the
        output given the numver of samples of the input.

        :param input_length: the number of samples of the input.
        :type input_length: int
        :returns: the maximum number of samples that will be written to the
            output.
        """
        raise NotImplementedError

    def read_from(self, reader):
        """Reads as many samples as possible from ``reader``, processes them,
        and returns the number of samples that were read.

        :param reader: a :class:`audiotsm.io.base.Reader`.
        :returns: the number of samples that were read from ``reader``.
        """
        raise NotImplementedError

    def run(self, reader, writer, flush=True):
        """Runs the TSM procedure on the content of ``reader`` and writes the
        output to ``writer``.

        :param reader: a :class:`audiotsm.io.base.Reader`.
        :param writer: a :class:`audiotsm.io.base.Writer`.
        :param flush: ``True`` if there is no more data to process.
        :type flush: bool, optional
        """
        finished = False
        while not (finished and reader.empty):
            self.read_from(reader)
            _, finished = self.write_to(writer)

        if flush:
            finished = False
            while not finished:
                _, finished = self.flush_to(writer)

            self.clear()

    def set_speed(self, speed):
        """Sets the speed ratio.

        :param speed: the speed ratio by which the speed of the signal will be
            multiplied (for example, if ``speed`` is set to 0.5, the output
            signal will be half as fast as the input signal).
        :type speed: float
        """
        raise NotImplementedError

    def write_to(self, writer):
        """Writes as many result samples as possible to ``writer``.

        :param writer: a :class:`audiotsm.io.base.Writer`.
        :returns: a tuple (``n``, ``finished``), with:

            - ``n`` the number of samples that were written to ``writer``
            - ``finished`` a boolean that is ``True`` when there are no samples
              remaining to write. In this case, the
              :func:`~audiotsm.base.tsm.TSM.read_from` method should be called
              to add new input samples, or, if there are no remaining input
              samples, the :func:`~audiotsm.base.tsm.TSM.flush_to` method
              should be called to get the last output samples.
        :rtype: (int, bool)
        """
        raise NotImplementedError
