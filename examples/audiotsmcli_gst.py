#!/usr/bin/env python

"""
Change the speed of an audio file without changing its pitch (with GStreamer).
"""

import argparse
import os
import sys
import gi
gi.require_version('Gst', '1.0')

# pylint: disable=wrong-import-position
from gi.repository import Gst, GObject
Gst.init(sys.argv)
import audiotsm.gstreamer.wsola  # pylint: disable=unused-import
# pylint: enable=wrong-import-position


class Pipeline(Gst.Pipeline):
    """A gstreamer pipeline that changes the speed of an audio file, write the
    output to another file, and quit the main gobject loop with this is done.

    :param tsm_description: the description used to create the tsm element of
        the pipeline. This will be used as input of the
        :func:`Gst.parse_launch` function.
    """
    def __init__(self, tsm_description="audiotsm-wsola"):
        super().__init__()

        self._speed = 0

        # Create the playbin, that will handle the decoding of the audio files
        self.playbin = Gst.ElementFactory.make('playbin', 'playbin')
        self.add(self.playbin)

        # Create the audiotsm bin, that will handle the TSM
        audiotsmbin = Gst.Bin('audiotsm')

        # Create the elements of the audiotsm bin, add them, and link them
        self.tsm = Gst.parse_launch(tsm_description)
        converter = Gst.ElementFactory.make('audioconvert', 'converter')
        encoder = Gst.ElementFactory.make('wavenc', 'encoder')
        self.sink = Gst.ElementFactory.make('filesink', 'sink')

        audiotsmbin.add(self.tsm)
        audiotsmbin.add(converter)
        audiotsmbin.add(encoder)
        audiotsmbin.add(self.sink)

        self.tsm.link(converter)
        converter.link(encoder)
        encoder.link(self.sink)

        # Add the sink pad of the TSM plugin to the audiotsm bin.
        self.tsm_sink_pad = Gst.GhostPad.new(
            'sink', self.tsm.get_static_pad('sink'))
        audiotsmbin.add_pad(self.tsm_sink_pad)

        # And link it to the playbin
        self.playbin.set_property("audio-sink", audiotsmbin)

        bus = self.get_bus()
        bus.add_signal_watch()
        bus.connect("message::error", self._on_error)
        bus.connect("message::eos", self._on_eos)

    def _on_error(self, _, message):
        """Called when there is an error during the playback."""
        # pylint: disable=no-self-use
        err, debug = message.parse_error()
        print("Error: %s" % err, debug)
        sys.exit()

    def _on_eos(self, _1, _2):
        """Called when the end of the audio file is reached."""
        # pylint: disable=no-self-use
        sys.exit()

    def set_speed(self, speed):
        """Set the speed ratio."""
        self._speed = speed

    def save(self, path):
        """Save the output of the TSM procedure to path, then quit the GObject
        loop."""
        self.sink.set_property('location', path)
        self.set_state(Gst.State.PAUSED)
        self.get_state(Gst.CLOCK_TIME_NONE)

        self.playbin.seek(self._speed, Gst.Format.BYTES, Gst.SeekFlags.FLUSH,
                          Gst.SeekType.SET, 0, Gst.SeekType.NONE, -1)

        self.set_state(Gst.State.PLAYING)

    def set_src_uri(self, uri):
        """Set the uri of the source audio file."""
        self.playbin.set_property("uri", uri)


def main():
    """Change the speed of an audio file without changing its pitch."""

    parser = argparse.ArgumentParser(description=(
        "Change the speed of an audio file without changing its pitch."))
    parser.add_argument(
        '-s', '--speed', metavar="S", type=float, default=1.,
        help="Set the speed ratio (e.g 0.5 to play at half speed)")
    parser.add_argument(
        'input_filename', metavar='INPUT_FILENAME', type=str,
        help="The audio input file")
    parser.add_argument(
        'output_filename', metavar='OUTPUT_FILENAME', type=str,
        help="The audio output file")

    args = parser.parse_args()

    if not os.path.isfile(args.input_filename):
        parser.error(
            'The input file "{}" does not exist.'.format(args.input_filename))

    pipeline = Pipeline()
    pipeline.set_speed(args.speed)
    pipeline.set_src_uri('file:///' + os.path.realpath(args.input_filename))
    pipeline.save(args.output_filename)

    loop = GObject.MainLoop()
    loop.run()


if __name__ == '__main__':
    main()
