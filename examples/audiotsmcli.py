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
from audiotsm.io.wav import WavReader, WavWriter


def main():
    """Change the speed of an audio file without changing its pitch."""

    # Parse command line arguments
    parser = argparse.ArgumentParser(description=(
        "Change the speed of an audio file without changing its pitch."))
    parser.add_argument('-s', '--speed', metavar="S", type=float, default=1.,
                        help=("Set the speed ratio (e.g 0.5 to play at half "
                              "speed)"))
    parser.add_argument('-l', '--frame-length', metavar='N', type=int,
                        default=None, help=("Set the frame length to N."))
    parser.add_argument('-a', '--analysis-hop', metavar='N', type=int,
                        default=None, help=("Set the analysis hop to N."))
    parser.add_argument('--synthesis-hop', metavar='N', type=int, default=None,
                        help=("Set the synthesis hop to N."))
    parser.add_argument('input_filename', metavar='INPUT_FILENAME', type=str,
                        help=("The audio input file"))
    parser.add_argument('output_filename', metavar='OUTPUT_FILENAME', type=str,
                        help=("The audio output file"))

    args = parser.parse_args()

    if not os.path.isfile(args.input_filename):
        parser.error(
            'The input file "{}" does not exist.'.format(args.input_filename))

    # Get TSM method parameters
    parameters = {}
    if args.speed is not None:
        parameters['speed'] = args.speed
    if args.frame_length is not None:
        parameters['frame_length'] = args.frame_length
    if args.analysis_hop is not None:
        parameters['analysis_hop'] = args.analysis_hop
    if args.speed is not None:
        parameters['speed'] = args.speed

    # Get input and output files
    input_filename = args.input_filename
    output_filename = args.output_filename

    # Run the TSM procedure
    with WavReader(input_filename) as reader:
        channels = reader.channels
        with WavWriter(output_filename, channels, reader.samplerate) as writer:
            tsm = ola(channels, **parameters)

            finished = False
            while not (finished and reader.empty):
                tsm.read_from(reader)
                _, finished = tsm.write_to(writer)

            finished = False
            while not finished:
                _, finished = tsm.flush_to(writer)


if __name__ == "__main__":
    main()
