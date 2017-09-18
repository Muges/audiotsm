# -*- coding: utf-8 -*-

"""
The :mod:`audiotsm.gstreamer.ola` module implements an audio filter allowing to
use the OLA procedure with gstreamer.
"""

import gi
gi.require_version('Gst', '1.0')

# pylint: disable=wrong-import-position
from gi.repository import GObject, Gst
from audiotsm import ola
from .base import GstTSM
# pylint: enable=wrong-import-position


class OLA(GstTSM):
    """OLA gstreamer audio filter."""
    __gstmetadata__ = (
        'OLA time-scale modification', 'Transform',
        'Change the speed of an audio stream with the OLA procedure',
        'Muges'
    )

    plugin_name = "audiotsm-ola"
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

    def create_tsm(self, channels):
        parameters = {}
        if self.frame_length > 0:
            parameters['frame_length'] = self.frame_length
        if self.synthesis_hop > 0:
            parameters['synthesis_hop'] = self.synthesis_hop

        return ola(channels, **parameters)


OLA.register()

# Register the plugin to make it usable outside python, e.g. with the
# following commands (this does not seem to work):
# export GST_PLUGIN_PATH=$PWD/audiotsm/gstreamer/
# gst-launch-1.0 fakesrc num-buffers=10 ! audiotsm-ola ! fakesink
_OLA_TYPE = GObject.type_register(OLA)
__gstelementfactory__ = (OLA.plugin_name, Gst.Rank.NONE, _OLA_TYPE)
