# -*- coding: utf-8 -*-

"""
The :mod:`~audiotsm.gstreamer.wsola` module implements an audio filter
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

    def create_tsm(self, channels, speed):
        return wsola(channels, speed)


WSOLA.register()

# Register the plugin to make it usable outside python, e.g. with the
# following commands (this does not seem to work):
# export GST_PLUGIN_PATH=$PWD/audiotsm/gstreamer/
# gst-launch-1.0 fakesrc num-buffers=10 ! audiotsm-wsola ! fakesink
WSOLA_TYPE = GObject.type_register(WSOLA)
__gstelementfactory__ = (WSOLA.plugin_name, Gst.Rank.NONE, WSOLA_TYPE)
