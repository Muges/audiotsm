#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
audiotsmcli
~~~~~~~~~~~

Change the speed of an audio file without changing its pitch.
"""

import argparse
import os

from audiotsm.ola import ola
from audiotsm.io.sounddevice import StreamWriter
from audiotsm.io.wav import WavReader, WavWriter


def main():
    """Change the speed of an audio file without changing its pitch."""

    # Parse command line arguments
    parser = argparse.ArgumentParser(description=(
        "Change the speed of an audio file without changing its pitch."))
    parser.add_argument(
        '-s', '--speed', metavar="S", type=float, default=1.,
        help=("Set the speed ratio (e.g 0.5 to play at half speed)"))
    parser.add_argument(
        '-l', '--frame-length', metavar='N', type=int, default=None,
        help=("Set the frame length to N."))
    parser.add_argument(
        '-a', '--analysis-hop', metavar='N', type=int, default=None,
        help=("Set the analysis hop to N."))
    parser.add_argument(
        '--synthesis-hop', metavar='N', type=int, default=None,
        help=("Set the synthesis hop to N."))
    parser.add_argument(
        '-o', '--output', metavar='FILENAME', type=str, default=None,
        help=("Write the output in the wav file FILENAME."))
    parser.add_argument(
        'input_filename', metavar='INPUT_FILENAME', type=str,
        help=("The audio input file"))

    args = parser.parse_args()

    if not os.path.isfile(args.input_filename):
        parser.error(
            'The input file "{}" does not exist.'.format(args.input_filename))

    # Get TSM method parameters
    parameters = {}
    if args.speed:
        parameters['speed'] = args.speed
    if args.frame_length:
        parameters['frame_length'] = args.frame_length
    if args.analysis_hop:
        parameters['analysis_hop'] = args.analysis_hop
    if args.synthesis_hop:
        parameters['synthesis_hop'] = args.synthesis_hop

    reader = WavReader(args.input_filename)
    if args.output:
        writer = WavWriter(args.output, reader.channels, reader.samplerate)
    else:
        writer = StreamWriter(reader.channels, reader.samplerate)

    # Run the TSM procedure
    with reader:
        with writer:
            tsm = ola(reader.channels, **parameters)

            finished = False
            while not (finished and reader.empty):
                tsm.read_from(reader)
                _, finished = tsm.write_to(writer)

            finished = False
            while not finished:
                _, finished = tsm.flush_to(writer)


if __name__ == "__main__":
    main()
