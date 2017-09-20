# -*- coding: utf-8 -*-

"""
The :mod:`audiotsm.phasevocoder` module implements the phase vocoder time-scale
modification procedure.
"""

import numpy as np

from audiotsm.base import AnalysisSynthesisTSM, Converter
from audiotsm.utils.windows import hanning


class PhaseVocoderConverter(Converter):
    """A Converter implementing the phase vocoder time-scale modification
    procedure."""
    # pylint: disable=too-many-instance-attributes
    def __init__(self, channels, frame_length, analysis_hop, synthesis_hop):
        self._channels = channels
        self._frame_length = frame_length
        self._synthesis_hop = synthesis_hop
        self._analysis_hop = analysis_hop

        # Centers of the FFT frequency bins
        self._center_frequency = np.fft.rfftfreq(frame_length) * 2 * np.pi
        fft_length = len(self._center_frequency)

        self._first = True

        self._previous_phase = np.empty((channels, fft_length))
        self._output_phase = np.empty((channels, fft_length))

        # Buffer used to compute the phase increment and the instantaneous
        # frequency
        self._buffer = np.empty(fft_length)

    def clear(self):
        self._first = True

    def convert_frame(self, frame):
        # pylint: disable=arguments-differ
        for k in range(0, self._channels):
            # Compute the FFT of the analysis frame
            stft = np.fft.rfft(frame[k])
            amplitude = np.abs(stft)
            phase = np.angle(stft)
            del stft

            if self._first:
                # Leave the first frame unchanged
                np.copyto(self._output_phase[k], phase)
                np.copyto(self._previous_phase[k], phase)
                del phase
                del amplitude
                continue

            # Compute the phase increment
            np.copyto(self._buffer, (
                phase - self._previous_phase[k] -
                self._analysis_hop * self._center_frequency
            ))

            # Unwrap the phase increment
            self._buffer += np.pi
            self._buffer %= 2 * np.pi
            self._buffer -= np.pi

            # Save the phase for the next analysis frame
            np.copyto(self._previous_phase[k], phase)
            del phase

            # Compute the instantaneous frequency (in the same buffer, since
            # the phase increment wont be required after that)
            self._buffer /= self._analysis_hop
            self._buffer += self._center_frequency

            self._output_phase[k] += self._synthesis_hop * self._buffer

            # Compute the new stft
            output_stft = amplitude * np.exp(1j * self._output_phase[k])
            del amplitude

            np.copyto(frame[k], np.fft.irfft(output_stft).real)

        self._first = False

        return frame

    def set_analysis_hop(self, analysis_hop):
        self._analysis_hop = analysis_hop


def phasevocoder(channels, speed=1., frame_length=2048, analysis_hop=None,
                 synthesis_hop=None):
    """Returns a :class:`~audiotsm.base.tsm.TSM` object implementing the phase
    vocoder time-scale modification procedure.

    In most cases, you should not need to set the ``frame_length``, the
    ``analysis_hop`` or the ``synthesis_hop``. If you want to fine tune these
    parameters, you can check the documentation of the
    :class:`~audiotsm.base.analysis_synthesis.AnalysisSynthesisTSM` class to
    see what they represent.

    :param channels: the number of channels of the input signal.
    :type channels: int
    :param speed: the speed ratio by which the speed of the signal will be
        multiplied (for example, if ``speed`` is set to 0.5, the output signal
        will be half as fast as the input signal).
    :type speed: float, optional
    :param frame_length: the length of the frames.
    :type frame_length: int, optional
    :param analysis_hop: the number of samples between two consecutive analysis
        frames (``speed * synthesis_hop`` by default). If ``analysis_hop`` is
        set, the ``speed`` parameter will be ignored.
    :type analysis_hop: int, optional
    :param synthesis_hop: the number of samples between two consecutive
        synthesis frames (``frame_length // 4`` by default).
    :type synthesis_hop: int, optional
    :returns: a :class:`audiotsm.base.tsm.TSM` object
    """
    if synthesis_hop is None:
        synthesis_hop = frame_length // 4

    if analysis_hop is None:
        analysis_hop = int(synthesis_hop * speed)

    analysis_window = hanning(frame_length)
    synthesis_window = hanning(frame_length)

    converter = PhaseVocoderConverter(channels, frame_length, analysis_hop,
                                      synthesis_hop)

    return AnalysisSynthesisTSM(
        converter, channels, frame_length, analysis_hop, synthesis_hop,
        analysis_window, synthesis_window)
