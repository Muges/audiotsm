# -*- coding: utf-8 -*-

"""
The :mod:`audiotsm.phasevocoder` module implements the phase vocoder time-scale
modification procedure.
"""

import numpy as np

from audiotsm.base import AnalysisSynthesisTSM, Converter
from audiotsm.utils.windows import hanning


def find_peaks(amplitude):
    """Find the peaks in an array.

    A value is considered to be a peak if it is higher than its four closest
    neighbours.

    :param amplitude: an array of floats of shape ``(n,)``.
    :type amplitude: :class:`numpy.ndarray`
    :returns: an array ``a`` of bools of shape ``(n,)``, where ``a[i]`` is
        ``True`` if there is a peak in the ``amplitude`` array at index ``i``.
    """
    # Pad the array with -1 at the beginning and the end to avoid overflows.
    padded = np.concatenate((-np.ones(2), amplitude, -np.ones(2)))

    # Shift the array by one/two values to the left/right
    shifted_l2 = padded[:-4]
    shifted_l1 = padded[1:-3]
    shifted_r1 = padded[3:-1]
    shifted_r2 = padded[4:]

    # Compare the original array with the shifted versions.
    peaks = ((amplitude >= shifted_l2) & (amplitude >= shifted_l1) &
             (amplitude >= shifted_r1) & (amplitude >= shifted_r2))

    return peaks


def all_peaks(amplitude):
    """A peak finder that considers all values to be peaks.

    This is used for the phase vocoder without phase locking.
    :param amplitude: an array of floats of shape ``(n,)``.
    :type amplitude: :class:`numpy.ndarray`
    :returns: an array ``a`` of bools of shape ``(n,)``, where ``a[i]`` is
        ``True`` if there is a peak in the ``amplitude`` array at index ``i``.
    """
    return np.ones_like(amplitude, dtype=bool)


def get_closest_peaks(peaks):
    """Returns an array containing the index of the closest peak of each index.

    :param peaks: an array of bools of shape ``(n,)``, as returned by
        :func:`find_peaks`.
    :type peaks: :class:`numpy.ndarray`
    :returns: an array ``a`` of ints of shape ``(n,)``, where ``a[i]`` is the
        index of the peak that is closest to ``i``.
    """
    closest_peak = np.empty_like(peaks, dtype=int)
    previous = -1
    for i, is_peak in enumerate(peaks):
        if is_peak:
            if previous >= 0:
                closest_peak[previous:(previous + i) // 2 + 1] = previous
                closest_peak[(previous + i) // 2 + 1:i] = i
            else:
                closest_peak[:i] = i
            previous = i
    closest_peak[previous:] = previous

    return closest_peak


class PhaseVocoderConverter(Converter):
    """A Converter implementing the phase vocoder time-scale modification
    procedure."""
    # pylint: disable=too-many-instance-attributes
    def __init__(self, channels, frame_length, analysis_hop, synthesis_hop,
                 peak_finder):
        # pylint: disable=too-many-arguments
        self._channels = channels
        self._frame_length = frame_length
        self._synthesis_hop = synthesis_hop
        self._analysis_hop = analysis_hop
        self._find_peaks = peak_finder

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

            peaks = self._find_peaks(amplitude)
            closest_peak = get_closest_peaks(peaks)

            if self._first:
                # Leave the first frame unchanged
                self._output_phase[k, :] = phase
            else:
                # Compute the phase increment
                self._buffer[peaks] = (
                    phase[peaks] - self._previous_phase[k, peaks] -
                    self._analysis_hop * self._center_frequency[peaks]
                )

                # Unwrap the phase increment
                self._buffer[peaks] += np.pi
                self._buffer[peaks] %= 2 * np.pi
                self._buffer[peaks] -= np.pi

                # Compute the instantaneous frequency (in the same buffer,
                # since the phase increment wont be required after that)
                self._buffer[peaks] /= self._analysis_hop
                self._buffer[peaks] += self._center_frequency[peaks]

                self._buffer[peaks] *= self._synthesis_hop
                self._output_phase[k][peaks] += self._buffer[peaks]

                # Phase locking
                self._output_phase[k] = (
                    self._output_phase[k][closest_peak] +
                    phase - phase[closest_peak]
                )

                # Compute the new stft
                output_stft = amplitude * np.exp(1j * self._output_phase[k])

                frame[k, :] = np.fft.irfft(output_stft).real

            # Save the phase for the next analysis frame
            self._previous_phase[k, :] = phase
            del phase
            del amplitude

        self._first = False

        return frame

    def set_analysis_hop(self, analysis_hop):
        self._analysis_hop = analysis_hop


class PhaseLocking(object):
    """Enumeration of phase locking strategies."""
    # pylint: disable=too-few-public-methods

    NONE = 0
    """No phase locking."""

    IDENTITY = 1
    """Identity phase locking."""

    @classmethod
    def from_str(cls, name):
        """Returns a phase locking strategy given its name."""
        if name.lower() == 'none':
            return cls.NONE
        elif name.lower() == 'identity':
            return cls.IDENTITY
        else:
            raise ValueError(
                'Invalid phase locking name: "{}"'.format(name))


def phasevocoder(channels, speed=1., frame_length=2048, analysis_hop=None,
                 synthesis_hop=None, phase_locking=PhaseLocking.IDENTITY):
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
    :param phase_locking: a phase locking strategy.
    :type phase_locking: :class:`PhaseLocking`, optional
    :returns: a :class:`audiotsm.base.tsm.TSM` object
    """
    # pylint: disable=too-many-arguments
    if synthesis_hop is None:
        synthesis_hop = frame_length // 4

    if analysis_hop is None:
        analysis_hop = int(synthesis_hop * speed)

    analysis_window = hanning(frame_length)
    synthesis_window = hanning(frame_length)

    if phase_locking == PhaseLocking.NONE:
        # No phase locking: all freqyency bins are considered to be peaks
        peak_finder = all_peaks
    elif phase_locking == PhaseLocking.IDENTITY:
        peak_finder = find_peaks
    else:
        raise ValueError(
            'Invalid phase_locking value: "{}"'.format(phase_locking))

    converter = PhaseVocoderConverter(channels, frame_length, analysis_hop,
                                      synthesis_hop, peak_finder)

    return AnalysisSynthesisTSM(
        converter, channels, frame_length, analysis_hop, synthesis_hop,
        analysis_window, synthesis_window)
