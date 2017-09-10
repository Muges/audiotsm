# -*- coding: utf-8 -*-

"""
The :mod:`audiotsm.io.wav` module provides a :class:`~audiotsm.io.base.Reader`
and a :class:`~audiotsm.io.base.Writer` allowing to use wav files as input or
output of a :class:`~audiotsm.base.tsm.TSM` object.
"""

import wave
import numpy as np

from . import base


class WavReader(base.Reader):
    """A :class:`~audiotsm.io.base.Reader` allowing to use a wav file as input
    of a :class:`~audiotsm.base.tsm.TSM` object.

    You should close the :class:`~audiotsm.io.wav.WavReader` after using it
    with the :func:`~audiotsm.io.wav.WavReader.close` method, or use it in a
    ``with`` statement as follow::

        with WavReader(filename) as reader:
            # use reader...

    :param filename: the name of an existing wav file.
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

    def skip(self, n):
        current_pos = self._reader.tell()
        new_pos = min(current_pos + n, self._reader.getnframes())

        self._reader.setpos(new_pos)

        return new_pos - current_pos

    def __enter__(self):
        return self

    def __exit__(self, _1, _2, _3):
        self.close()


class WavWriter(base.Writer):
    """A :class:`~audiotsm.io.base.Writer` allowing to use a wav file as output
    of a :class:`~audiotsm.base.tsm.TSM` object.

    You should close the :class:`~audiotsm.io.wav.WavWriter` after using it
    with the :func:`~audiotsm.io.wav.WavWriter.close` method, or use it in a
    ``with`` statement as follow::

        with WavWriter(filename, 2, 44100) as writer:
            # use writer...

    :param filename: the name of the wav file (it will be overwritten if it
        already exists).
    :type filename: str
    :param channels: the number of channels of the signal.
    :type channels: int
    :param samplerate: the sampling rate of the signal.
    :type samplerate: int
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
