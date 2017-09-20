# -*- coding: utf-8 -*-

"""
The :mod:`audiotsm.gstreamer.phasevocoder` module implements an audio filter
allowing to use the phase vocoder procedure with gstreamer.
"""

import gi
gi.require_version('Gst', '1.0')

# pylint: disable=wrong-import-position
from gi.repository import GObject, Gst
from audiotsm import phasevocoder
from .base import GstTSM
# pylint: enable=wrong-import-position


class PhaseVocoder(GstTSM):
    """Phase vocoder gstreamer audio filter."""
    __gstmetadata__ = (
        'Phase vocoder time-scale modification', 'Transform',
        'Change the speed of an audio stream with the phase vocoder procedure',
        'Muges'
    )

    plugin_name = "audiotsm-phase-vocoder"
    """The plugin name, to be used in ``Gst.ElementFactory.make``."""

    frame_length = GObject.Property(type=int, default=-1,
                                    flags=GObject.ParamFlags.WRITABLE)
    """The length of the frames.

    This is a write-only attribute, that will only take effect the next time
    the audio filter is setup (usually on the next song)."""

    synthesis_hop = GObject.Property(type=int, default=-1,
                                     flags=GObject.ParamFlags.WRITABLE)
    """The number of samples between two consecutive synthesis frames.

    This is a write-only attribute, that will only take effect the next time
    the audio filter is setup (usually on the next song)."""

    tolerance = GObject.Property(type=int, default=-1,
                                 flags=GObject.ParamFlags.WRITABLE)
    """The maximum number of samples that the analysis frame can be shifted.

    This is a write-only attribute, that will only take effect the next time
    the audio filter is setup (usually on the next song)."""

    def create_tsm(self, channels):
        parameters = {}
        if self.frame_length > 0:
            parameters['frame_length'] = self.frame_length
        if self.synthesis_hop > 0:
            parameters['synthesis_hop'] = self.synthesis_hop
        if self.tolerance >= 0:
            parameters['tolerance'] = self.tolerance

        return phasevocoder(channels, **parameters)


PhaseVocoder.register()

# Register the plugin to make it usable outside python, e.g. with the
# following commands (this does not seem to work):
# export GST_PLUGIN_PATH=$PWD/audiotsm/gstreamer/
# gst-launch-1.0 fakesrc num-buffers=10 ! audiotsm-phase-vocoder ! fakesink
_PV_TYPE = GObject.type_register(PhaseVocoder)
__gstelementfactory__ = (PhaseVocoder.plugin_name, Gst.Rank.NONE, _PV_TYPE)
