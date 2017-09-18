# -*- coding: utf-8 -*-

"""
The :mod:`audiotsm.gstreamer.wsola` module implements an audio filter
allowing to use the WSOLA procedure with gstreamer.
"""

import gi
gi.require_version('Gst', '1.0')

# pylint: disable=wrong-import-position
from gi.repository import GObject, Gst
from audiotsm import wsola
from .base import GstTSM
# pylint: enable=wrong-import-position


class WSOLA(GstTSM):
    """WSOLA gstreamer audio filter."""
    __gstmetadata__ = (
        'WSOLA time-scale modification', 'Transform',
        'Change the speed of an audio stream with the WSOLA procedure',
        'Muges'
    )

    plugin_name = "audiotsm-wsola"
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

        return wsola(channels, **parameters)


WSOLA.register()

# Register the plugin to make it usable outside python, e.g. with the
# following commands (this does not seem to work):
# export GST_PLUGIN_PATH=$PWD/audiotsm/gstreamer/
# gst-launch-1.0 fakesrc num-buffers=10 ! audiotsm-wsola ! fakesink
_WSOLA_TYPE = GObject.type_register(WSOLA)
__gstelementfactory__ = (WSOLA.plugin_name, Gst.Rank.NONE, _WSOLA_TYPE)
