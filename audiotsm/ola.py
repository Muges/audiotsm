# -*- coding: utf-8 -*-

"""
The :mod:`audiotsm.ola` module implements the OLA (Overlap-Add) time-scale
modification procedure.
"""

from audiotsm.base import AnalysisSynthesisTSM, Converter
from audiotsm.utils.windows import hanning


class OLAConverter(Converter):
    """A Converter implementing the OLA (Overlap-Add) time-scale modification
    procedure."""
    def convert_frame(self, analysis_frame):
        return analysis_frame


def ola(channels, speed=1., frame_length=256, analysis_hop=None,
        synthesis_hop=None):
    """Returns a :class:`~audiotsm.base.tsm.TSM` object implementing the OLA
    (Overlap-Add) time-scale modification procedure.

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
        synthesis frames (``frame_length // 2`` by default).
    :type synthesis_hop: int, optional
    :returns: a :class:`audiotsm.base.tsm.TSM` object
    """
    if synthesis_hop is None:
        synthesis_hop = frame_length // 2

    if analysis_hop is None:
        analysis_hop = int(synthesis_hop * speed)

    analysis_window = None
    synthesis_window = hanning(frame_length)

    converter = OLAConverter()

    return AnalysisSynthesisTSM(
        converter, channels, frame_length, analysis_hop, synthesis_hop,
        analysis_window, synthesis_window)
