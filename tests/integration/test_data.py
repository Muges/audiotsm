# -*- coding: utf-8 -*-

"""
Tests the TSM procedures on real data.
"""

import os
import shutil
import pytest

from audiotsm import ola, wsola
from audiotsm.io.wav import WavReader, WavWriter
from audiotsm.io.array import ArrayWriter

EXAMPLES_DIR = os.path.join("build", "ghpages", "examples")


def create_tsm(name, channels, speed):
    """Create a TSM object given the method name and its parameters."""
    if name == "wsola":
        return wsola(channels, speed)
    if name == "ola":
        return ola(channels, speed)

    raise ValueError("unknown TSM method: {}".format(name))


def test_data(data_file, speed, tsm_name, save):
    """Test the TSM procedures on real data."""
    reader = None
    writer = None

    try:
        # Create the reader
        reader = WavReader(data_file)

        # Create the writer
        if save:
            # pylint: disable=no-member
            rel_path = os.path.relpath(data_file, pytest.DATA_DIR)
            # pylint: enable=no-member

            # Copy original file to "orig" directory
            orig_file = os.path.join(EXAMPLES_DIR, "orig", rel_path)
            orig_dir = os.path.dirname(orig_file)
            if not os.path.isdir(orig_dir):
                os.makedirs(orig_dir)
            if not os.path.isfile(orig_file):
                shutil.copy2(data_file, orig_file)

            # Generate output file path
            speed_dir = "speed-{:.2f}".format(speed)
            name = os.path.splitext(rel_path)[0]
            output_name = "{}_{}.wav".format(name, tsm_name)
            output_file = os.path.join(EXAMPLES_DIR, speed_dir, output_name)
            output_dir = os.path.dirname(output_file)
            if not os.path.isdir(output_dir):
                os.makedirs(output_dir)

            writer = WavWriter(output_file, reader.channels, reader.samplerate)
        else:
            writer = ArrayWriter(reader.channels)

        # Create and run the TSM
        tsm = create_tsm(tsm_name, reader.channels, speed)
        tsm.run(reader, writer)

    finally:
        # Close files
        if reader:
            reader.close()
        if save and writer:
            writer.close()
