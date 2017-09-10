# -*- coding: utf-8 -*-

"""
The :mod:`audiotsm.io.stream` module provides a
:class:`~audiotsm.io.base.Writer` allowing to play the output of a
:class:`~audiotsm.base.tsm.TSM` object in real-time.
"""


import numpy as np
from sounddevice import OutputStream

from . import base


class StreamWriter(base.Writer):
    """A :class:`~audiotsm.io.base.Writer` allowing to play the output of a
    :class:`~audiotsm.base.tsm.TSM` object directly.

    You should stop the :class:`~audiotsm.io.stream.StreamWriter` after using
    it with the :func:`~audiotsm.io.stream.StreamWriter.stop` method, or use it
    in a ``with`` statement as follow::

        with WavWriter(2, 44100) as writer:
            # use writer...

    :param channels: the number of channels of the signal.
    :type channels: int
    :param samplerate: the sampling rate of the signal.
    :type samplerate: int
    :param attrs: additional parameters used to create the
        :class:`sounddevice.OutputStream` that is used by the
        :class:`~audiotsm.io.stream.StreamWriter`.
    """
    def __init__(self, channels, samplerate, **attrs):
        self._channels = channels

        self._stream = OutputStream(samplerate=samplerate, channels=channels,
                                    **attrs)
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
