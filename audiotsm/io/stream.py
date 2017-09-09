# -*- coding: utf-8 -*-

"""
audiotsm.io.stream
~~~~~~~~~~~~~~~~~~

This module provides a Writer allowing to play the output of a TSM object
directly.
"""


import numpy as np
from sounddevice import OutputStream

from . import base


class StreamWriter(base.Writer):
    """A Writer allowing to play the output of a TSM object directly."""
    def __init__(self, channels, samplerate):
        self._channels = channels

        self._stream = OutputStream(samplerate=samplerate, channels=channels)
        self._stream.start()

    @property
    def channels(self):
        return self._channels

    def write(self, buffer):
        if buffer.shape[0] != self.channels:
            raise ValueError("the buffer should have the same number of "
                             "channels as the WavWriter")

        self._stream.write(np.ascontiguousarray(buffer.T))

        return buffer.shape[1]

    def stop(self):
        """Stop the stream."""
        self._stream.stop()

    def __enter__(self):
        return self

    def __exit__(self, _1, _2, _3):
        self.stop()
