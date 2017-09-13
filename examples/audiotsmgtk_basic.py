#!/usr/bin/env python

"""
A simple gtk audio player using audiotsm with gstreamer.
"""

import os
import sys
import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')

# pylint: disable=wrong-import-position
from gi.repository import Gst, GObject, Gtk
import audiotsm.gstreamer.wsola  # pylint: disable=unused-import
# pylint: enable=wrong-import-position


class MainWindow(Gtk.Window):
    """The main window of audiotsmgtk-basic."""
    def __init__(self):
        super().__init__(Gtk.WindowType.TOPLEVEL)
        self.set_title('audiotsmgtk-basic')
        self.set_default_size(400, 200)
        self.connect('destroy', Gtk.main_quit)

        # Play/pause button
        self.toggle_button = Gtk.Button('Start')
        self.toggle_button.connect('clicked', self.on_toggle)
        self.add(self.toggle_button)

        # Player
        self.player = Gst.Pipeline.new('player')
        self.create_player()

    def create_player(self):
        """Create the gstreamer pipeline."""
        # Build the pipeline
        # For a basic tutorial on how to build one, see
        # http://brettviren.github.io/pygst-tutorial-org/pygst-tutorial.html
        source = Gst.ElementFactory.make('filesrc', 'source')
        decoder = Gst.ElementFactory.make('wavparse', 'decoder')
        conv = Gst.ElementFactory.make('audioconvert', 'converter')
        tsm = Gst.ElementFactory.make('audiotsm-wsola', 'tsm')
        sink = Gst.ElementFactory.make('autoaudiosink', 'sink')

        if not tsm:
            raise RuntimeError('unable to load audiotsm-wsola plugin')

        self.player.add(source)
        self.player.add(decoder)
        self.player.add(conv)
        self.player.add(tsm)
        self.player.add(sink)

        source.link(decoder)
        decoder.link(conv)
        conv.link(tsm)
        tsm.link(sink)

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

    def open_file(self, path):
        """Open a wav file."""
        if os.path.isfile(path):
            uri = os.path.realpath(path)
            source = self.player.get_by_name("source")
            source.set_property("location", uri)

    def on_toggle(self, _):
        """Method called when the play/pause button is clicked."""
        if self.toggle_button.get_label() == "Start":
            self.toggle_button.set_label("Stop")
            self.player.set_state(Gst.State.PLAYING)
        else:
            self.player.set_state(Gst.State.NULL)
            self.toggle_button.set_label("Start")

    def on_message(self, _, message):
        """Method called when there is a message on the bus of the gstreamer
        pipeline."""
        if message.type == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
            self.toggle_button.set_label("Start")
        elif message.type == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            self.toggle_button.set_label("Start")
            err, debug = message.parse_error()
            print("Error: %s" % err, debug)


def main():
    """Run audiotsmgtk-basic."""
    if len(sys.argv) <= 1:
        print('usage: audiotsmgtk-basic.py <wavfile>')
        return

    Gst.init(sys.argv)

    window = MainWindow()
    window.open_file(sys.argv[1])

    window.show_all()

    GObject.threads_init()
    Gtk.main()


if __name__ == "__main__":
    main()
