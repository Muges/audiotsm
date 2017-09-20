#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
audiotsmcli
~~~~~~~~~~~

Change the speed of an audio file without changing its pitch.
"""

import argparse
import os

from audiotsm import ola, wsola, phasevocoder
from audiotsm.io.stream import StreamWriter
from audiotsm.io.wav import WavReader, WavWriter


def create_writer(output, reader):
    """Create a Writer with the same parameters as ``reader``.

    :param output: the path of the output wav file. If it is None, the output
        will be played with a StreamWriter.
    :type output: str
    :param reader: the WavReader used as input of the TSM
    """
    if output:
        return WavWriter(output, reader.channels, reader.samplerate)

    return StreamWriter(reader.channels, reader.samplerate)


def create_tsm(name, channels, parameters):
    """Create a TSM object given the method name and its parameters."""
    if name == "ola":
        return ola(channels, **parameters)
    if name == "wsola":
        return wsola(channels, **parameters)
    if name == "phasevocoder":
        return phasevocoder(channels, **parameters)

    raise ValueError("unknown TSM method: {}".format(name))


def main():
    """Change the speed of an audio file without changing its pitch."""

    # Parse command line arguments
    parser = argparse.ArgumentParser(description=(
        "Change the speed of an audio file without changing its pitch."))
    parser.add_argument(
        '-s', '--speed', metavar="S", type=float, default=1.,
        help="Set the speed ratio (e.g 0.5 to play at half speed)")
    parser.add_argument(
        '-m', '--method', type=str, default="wsola",
        help="Select the TSM method (ola, wsola, or phasevocoder)")
    parser.add_argument(
        '-l', '--frame-length', metavar='N', type=int, default=None,
        help="Set the frame length to N.")
    parser.add_argument(
        '-a', '--analysis-hop', metavar='N', type=int, default=None,
        help="Set the analysis hop to N.")
    parser.add_argument(
        '--synthesis-hop', metavar='N', type=int, default=None,
        help="Set the synthesis hop to N.")
    parser.add_argument(
        '-t', '--tolerance', metavar='N', type=int, default=None,
        help="Set the tolerance to N (only used when method is set wsola).")
    parser.add_argument(
        '-o', '--output', metavar='FILENAME', type=str, default=None,
        help="Write the output in the wav file FILENAME.")
    parser.add_argument(
        'input_filename', metavar='INPUT_FILENAME', type=str,
        help="The audio input file")

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
    if args.tolerance is not None and args.method == "wsola":
        parameters['tolerance'] = args.tolerance

    # Run the TSM procedure
    with WavReader(args.input_filename) as reader:
        with create_writer(args.output, reader) as writer:
            tsm = create_tsm(args.method, reader.channels, parameters)
            tsm.run(reader, writer)


if __name__ == "__main__":
    main()
