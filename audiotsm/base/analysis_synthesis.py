# -*- coding: utf-8 -*-

"""
The :mod:`audiotsm.base.analysis_synthesis` module provides a base class for
real-time analysis-synthesis based audio time-scale modification procedures.
"""

import numpy as np

from audiotsm.utils import (windows, CBuffer, NormalizeBuffer)
from .tsm import TSM

EPSILON = 0.0001


class AnalysisSynthesisTSM(TSM):
    """A :class:`audiotsm.base.tsm.TSM` for real-time analysis-synthesis based
    time-scale modification procedures.

    The basic principle of an analysis-synthesis based TSM procedure is to
    first decompose the input signal into short overlapping frames, called the
    analysis frames. The frames have a fixed length ``frame_length``, and are
    separated by ``analysis_hop`` samples, as illustrated below::

                 <--------frame_length--------><-analysis_hop->
       Frame 1:  [~~~~~~~~~~~~~~~~~~~~~~~~~~~~]
       Frame 2:                  [~~~~~~~~~~~~~~~~~~~~~~~~~~~~]
       Frame 3:                                  [~~~~~~~~~~~~~~~~~~~~~~~~~~~~]
       ...

    It then relocates the frames on the time axis by changing the distance
    between them (to ``synthesis_hop``), as illustrated below::

                 <--------frame_length--------><----synthesis_hop---->
       Frame 1:  [~~~~~~~~~~~~~~~~~~~~~~~~~~~~]
       Frame 2:                         [~~~~~~~~~~~~~~~~~~~~~~~~~~~~]
       Frame 3:                                               [~~~~~~~~~~~~~~~~~~~~~~~~~~~~]
       ...

    This changes the speed of the signal by the ratio ``analysis_hop /
    synthesis_hop`` (for example, if the ``synthesis_hop`` is twice the
    ``analysis_hop``, the output signal will be half as fast as the input
    signal).

    However this simple method introduces artifacts to the signal. These
    artifacts can be reduced by modifying the analysis frames by various
    methods. This is done by a ``converter`` object, which converts the
    analysis frames into modified frames called the synthesis frames.

    To further reduce the artifacts, window functions (the ``analysis_window``
    and the ``synthesis_window``) can be applied to the analysis frames and the
    synthesis frames in order to smooth the signal.

    Some TSM procedures (e.g. WSOLA-like methods) may need to have access to
    some samples preceeding or following an analysis frame to generate the
    synthesis frame. The `delta_before` and `delta_after` parameters allow to
    specify the numbers of samples needed before and after the analysis frame,
    so that they are available to the ``converter``.

    For more details on Time-Scale Modification procedures, I recommend reading
    "`A Review of Time-Scale Modification of Music Signals`_" by Jonathan
    Driedger and Meinard Müller.

    .. _A Review of Time-Scale Modification of Music Signals:
        http://www.mdpi.com/2076-3417/6/2/57

    :param converter: an object that implements the conversion of the analysis
        frames into synthesis frames.
    :type converter: :class:`Converter`
    :param channels: the number of channels of the input signal.
    :type channels: int
    :param frame_length: the length of the frames.
    :type frame_length: int
    :param analysis_hop: the number of samples between two consecutive analysis
        frames.
    :type analysis_hop: int
    :param synthesis_hop: the number of samples between two consecutive
        synthesis frames.
    :type synthesis_hop: int
    :param analysis_window: a window applied to the analysis frames
    :type analysis_window: :class:`numpy.ndarray`
    :param synthesis_window: a window applied to the synthesis frames
    :type synthesis_window: :class:`numpy.ndarray`
    :param delta_before: the number of samples preceding an analysis frame that
        the converter requires (this is usually 0, except for WSOLA-like
        methods)
    :type delta_before: int
    :param delta_after: the number of samples following an analysis frame that
        the converter requires (this is usually 0, except for WSOLA-like
        methods)
    :type delta_after: int
    """  # noqa: E501
    # pylint: disable=too-many-instance-attributes
    def __init__(self, converter, channels, frame_length, analysis_hop,
                 synthesis_hop, analysis_window, synthesis_window,
                 delta_before=0, delta_after=0):
        # pylint: disable=too-many-arguments
        self._converter = converter

        self._channels = channels
        self._frame_length = frame_length
        self._analysis_hop = analysis_hop
        self._synthesis_hop = synthesis_hop

        self._analysis_window = analysis_window
        self._synthesis_window = synthesis_window

        self._delta_before = delta_before
        self._delta_after = delta_after

        # When the analysis hop is larger than the frame length, some samples
        # from the input need to be skipped. self._skip_input_samples tracks
        # how many samples should be skipped before reading the analysis frame.
        self._skip_input_samples = 0

        # This attribute is used to start the output signal in the middle of a
        # frame, which should be the peek of the window function
        self._skip_output_samples = 0

        # Compute the normalize window
        self._normalize_window = windows.product(self._analysis_window,
                                                 self._synthesis_window)

        if self._normalize_window is None:
            self._normalize_window = np.ones(self._frame_length)

        # Initialize the buffers
        delta = self._delta_before + self._delta_after
        self._in_buffer = CBuffer(self._channels, self._frame_length + delta)
        self._analysis_frame = np.empty(
            (self._channels, self._frame_length + delta))
        self._out_buffer = CBuffer(self._channels, self._frame_length)
        self._normalize_buffer = NormalizeBuffer(self._frame_length)

        self.clear()

    def clear(self):
        # Clear the buffers
        self._in_buffer.remove(self._in_buffer.length)
        self._out_buffer.remove(self._out_buffer.length)
        self._out_buffer.right_pad(self._frame_length)
        self._normalize_buffer.remove(self._normalize_buffer.length)

        # Left pad the input with half a frame of zeros, and ignore that half
        # frame in the output. This makes the output signal start in the middle
        # of a frame, which should be the peak of the window function.
        self._in_buffer.write(np.zeros(
            (self._channels, self._delta_before + self._frame_length // 2)))
        self._skip_output_samples = self._frame_length // 2

        # Clear the converter
        self._converter.clear()

    def flush_to(self, writer):
        if self._in_buffer.remaining_length == 0:
            raise RuntimeError("There is still data to process in the input "
                               "buffer, flush_to method should only be called "
                               "when write_to returns True.")

        n = self._out_buffer.write_to(writer)
        if self._out_buffer.ready == 0:
            # The output buffer is empty
            self.clear()
            return n, True

        return n, False

    def get_max_output_length(self, input_length):
        input_length -= self._skip_input_samples
        if input_length <= 0:
            return 0

        n_frames = input_length // self._analysis_hop + 1
        return n_frames * self._synthesis_hop

    def _process_frame(self):
        """Read an analysis frame from the input buffer, process it, and write
        the result to the output buffer."""
        # Generate the analysis frame and discard the input samples that will
        # not be needed anymore
        self._in_buffer.peek(self._analysis_frame)
        self._in_buffer.remove(self._analysis_hop)

        # Apply the analysis window
        windows.apply(self._analysis_frame, self._analysis_window)

        # Convert the analysis frame into a synthesis frame
        synthesis_frame = self._converter.convert_frame(self._analysis_frame)

        # Apply the synthesis window
        windows.apply(synthesis_frame, self._synthesis_window)

        # Overlap and add the synthesis frame in the output buffer
        self._out_buffer.add(synthesis_frame)

        # The overlap and add step changes the volume of the signal. The
        # normalize_buffer is used to keep track of "how much of the input
        # signal was added" to each part of the output buffer, allowing to
        # normalize it.
        self._normalize_buffer.add(self._normalize_window)

        # Normalize the samples that are ready to be written to the output
        normalize = self._normalize_buffer.to_array(end=self._synthesis_hop)
        normalize[normalize < EPSILON] = 1
        self._out_buffer.divide(normalize)
        self._out_buffer.set_ready(self._synthesis_hop)
        self._normalize_buffer.remove(self._synthesis_hop)

    def read_from(self, reader):
        n = reader.skip(self._skip_input_samples)
        self._skip_input_samples -= n
        if self._skip_input_samples > 0:
            return n

        n += self._in_buffer.read_from(reader)

        if (self._in_buffer.remaining_length == 0 and
                self._out_buffer.remaining_length >= self._synthesis_hop):
            # The input buffer has enough data to process, and there is enough
            # space in the output buffer to store the output
            self._process_frame()

            # Skip output samples if necessary
            skipped = self._out_buffer.remove(self._skip_output_samples)
            self._out_buffer.right_pad(skipped)
            self._skip_output_samples -= skipped

            # Set the number of input samples to be skipped
            self._skip_input_samples = self._analysis_hop - self._frame_length
            if self._skip_input_samples < 0:
                self._skip_input_samples = 0

        return n

    def set_speed(self, speed):
        self._analysis_hop = int(self._synthesis_hop * speed)

    def write_to(self, writer):
        n = self._out_buffer.write_to(writer)
        self._out_buffer.right_pad(n)

        if (self._in_buffer.remaining_length > 0 and
                self._out_buffer.ready == 0):
            # There is not enough data to process in the input buffer, and the
            # output buffer is empty
            return n, True

        return n, False


class Converter(object):
    """A base class for objects implementing the conversion of analysis frames
    into synthesis frames."""

    def clear(self):
        """Clears the state of the Converter, making it ready to be used on
        another signal (or another part of a signal). It is called by the
        :func:`~audiotsm.base.tsm.TSM.clear` method and the constructor of
        :class:`AnalysisSynthesisTSM`."""
        # pylint: disable=no-self-use
        return

    def convert_frame(self, analysis_frame):
        """Converts an analysis frame into a synthesis frame.

        :param analysis_frame: a matrix of shape (``m``, ``delta_before +
            frame_length + delta_after``), with ``m`` the number of channels,
            containing the analysis frame and some samples before and after
            (as specified by the ``delta_before`` and ``delta_after``
            parameters of the :class:`AnalysisSynthesisTSM` calling the
            :class:`Converter`).

            ``analysis_frame[:, delta_before:-delta_after]`` contains the
            actual analysis frame (without the samples preceeding and following
            it).
        :type analysis_frame: :class:`numpy.ndarray`
        :returns: a synthesis frame represented as a :class:`numpy.ndarray` of
            shape (``m``, ``frame_length``), with ``m`` the number of channels.
        """
        raise NotImplementedError
