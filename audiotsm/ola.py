# -*- coding: utf-8 -*-

"""
audiotsm.ola
~~~~~~~~~~~~~

This module implements the OLA (Overlap-Add) time-scale modification procedure.
"""

from audiotsm.base import AnalysisSynthesisTSM, Converter
from audiotsm.utils.windows import hanning


class OLAConverter(Converter):
    """A Converter implementing the OLA (Overlap-Add) time-scale modification
    procedure."""
    def convert_frame(self, analysis_frame):
        return analysis_frame


def ola(channels=2, speed=1., frame_length=256, analysis_hop=None,
        synthesis_hop=None):
    """Returns a TSM object implementing the OLA (Overlap-Add) time-scale
    modification procedure.

    :param channels: (optional) the number of channels of the audio signal.
    :type channels: int
    :param speed: (optional) the speed ratio by which the speed of the signal
        will be multiplied (for example, 0.5 means the output will be half as
        fast as the input). It will be ignored if the analysis_hop argument is
        set.
    :type speed: float
    :param frame_length: (optional) the length of the frames.
    :type frame_length: int
    :param speed: (optional) the speed ratio by which the speed of the signal
        will be multiplied (for example, 0.5 means the output will be half as
        fast as the input). It will be ignored if the analysis_hop argument is
        set.
    :type speed: float
    :param analysis_hop: (optional) the number of samples between two
        consecutive analysis frames (``speed * synthesis_hop`` by default)
    :type analysis_hop: int
    :param synthesis_hop: (optional) the number of samples between two
        consecutive synthesis frames (half the frame_length by default)
    :type synthesis_hop: int
    :returns: a :class:`base.TSM` object
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
