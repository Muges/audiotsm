# -*- coding: utf-8 -*-

"""
audiotsm.io.wav
~~~~~~~~~~~~~~~

This module provides a Reader and a Writer allowing to use
wav files as input and output of a TSM object.
"""

import wave
import numpy as np

from . import base


class WavReader(base.Reader):
    """A Reader allowing to use a wav file as input of a TSM object.

    :param filename: a path to a wav file.
    :type filename: str
    """
    def __init__(self, filename):
        self._reader = wave.open(filename, 'rb')

    @property
    def channels(self):
        return self._reader.getnchannels()

    @property
    def empty(self):
        return self._reader.tell() == self._reader.getnframes()

    def close(self):
        """Close the wav file."""
        self._reader.close()

    def read(self, buffer):
        if buffer.shape[0] != self.channels:
            raise ValueError("the buffer should have the same number of "
                             "channels as the WavReader")

        frames = self._reader.readframes(buffer.shape[1])
        frames = np.frombuffer(frames, '<i2').astype(np.float32) / 32676

        # Separate channels
        frames = frames.reshape((-1, self.channels)).T

        n = frames.shape[1]
        np.copyto(buffer[:, :n], frames)
        del frames

        return n

    @property
    def samplerate(self):
        """The samplerate of the wav file."""
        return self._reader.getframerate()

    @property
    def samplewidth(self):
        """The sample width in bytes of the wav file."""
        return self._reader.getsamplewidth()

    def __enter__(self):
        return self

    def __exit__(self, _1, _2, _3):
        self.close()


class WavWriter(base.Writer):
    """A Writer allowing to use a wav file as output of a TSM object.

    :param filename: a path to a wav file.
    :type filename: str
    """
    def __init__(self, filename, channels, samplerate):
        self._writer = wave.open(filename, 'wb')
        self._channels = channels
        self._writer.setnchannels(channels)
        self._writer.setframerate(samplerate)
        self._writer.setsampwidth(2)

    @property
    def channels(self):
        return self._channels

    def close(self):
        """Close the wav file."""
        self._writer.close()

    def write(self, buffer):
        if buffer.shape[0] != self.channels:
            raise ValueError("the buffer should have the same number of "
                             "channels as the WavWriter")

        n = buffer.shape[1]
        frames = (buffer.T.reshape((-1,)) * 32676).astype(np.int16).tobytes()
        self._writer.writeframes(frames)
        del frames

        return n

    def __enter__(self):
        return self

    def __exit__(self, _1, _2, _3):
        self.close()
