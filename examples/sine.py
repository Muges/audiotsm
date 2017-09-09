#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
sine
~~~~

Run a TSM procedure on a signal generated with numpy.
"""
# pylint: disable=invalid-name

import numpy as np
import sounddevice as sd
from audiotsm import wsola
from audiotsm.io.array import ArrayReader, ArrayWriter


# The parameters of the input signal
length = 1  # in seconds
samplerate = 44100  # in Hz
frequency = 440  # an A4

# Generate the input signal
time = np.linspace(0, length, int(length * samplerate))
input_signal = np.sin(np.pi * frequency * time).reshape((1, -1))

# Run the TSM procedure
reader = ArrayReader(input_signal)
writer = ArrayWriter(channels=1)

tsm = wsola(channels=1, speed=0.5)
tsm.run(reader, writer)

# Play the output
# This example was written to show how to use an ArrayWriter. If you want to
# play the output of a TSM procedure you should use an
# audiotsm.io.stream.StreamWriter.
sd.play(np.ascontiguousarray(writer.data.T), samplerate, blocking=True)
