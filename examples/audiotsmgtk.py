#!/usr/bin/env python

"""
A simple gtk audio player using audiotsm with gstreamer.
"""

import os
import sys
import numpy as np
import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')

# pylint: disable=wrong-import-position
from gi.repository import Gst, GObject, Gtk
import audiotsm.gstreamer.wsola  # pylint: disable=unused-import
# pylint: enable=wrong-import-position


def get_icon_name(icon_names):
    """Return the first icon name that is available in the current GTK icon
    theme."""
    theme = Gtk.IconTheme.get_default()

    for icon_name in icon_names:
        if theme.has_icon(icon_name):
            return icon_name

    return ""


def format_time(time):
    """Format a time as "minutes:seconds"."""
    minutes, seconds = divmod(time // Gst.SECOND, 60)
    return "{}:{:02d}".format(minutes, seconds)


class Player(Gst.Pipeline):
    """A gstreamer pipeline that provides an easy-to-use player with a
    changeable playing speed.

    :param tsm_description: the description used to create the tsm element of
        the pipeline. This will be used as input of the
        :func:`Gst.parse_launch` function.

    Signals
    ~~~~~~~

    ``position-changed(position, duration)``
        Emitted at regular time interval during the playback.
    ``state-changed(state)``
        Emitted when the state of the player changes.
    """
    __gsignals__ = {
        'position-changed':
            (GObject.SIGNAL_RUN_FIRST, None, (GObject.TYPE_LONG,
                                              GObject.TYPE_LONG)),
        'state-changed':
            (GObject.SIGNAL_RUN_FIRST, None, (GObject.TYPE_INT,))
    }

    def __init__(self, tsm_description="audiotsm-wsola"):
        super().__init__()

        self._speed = 1.0
        self._speed_set = False

        # Create the playbin, that will handle the decoding of the audio files
        self.playbin = Gst.ElementFactory.make('playbin', 'playbin')
        self.add(self.playbin)

        # Create the audiotsm bin, that will handle the TSM
        audiotsmbin = Gst.Bin('audiotsm')

        # Create the elements of the audiotsm bin, add them, and link them
        self.tsm = Gst.parse_launch(tsm_description)
        converter = Gst.ElementFactory.make('audioconvert', 'converter')
        sink = Gst.ElementFactory.make('autoaudiosink', 'sink')

        audiotsmbin.add(self.tsm)
        audiotsmbin.add(converter)
        audiotsmbin.add(sink)

        self.tsm.link(converter)
        converter.link(sink)

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
        bus.connect("message::state-changed", self._on_state_changed)

        # The timer that will emit the position-changed signal
        self.position_timer = None

    def do_state_changed(self, *args):
        # pylint: disable=missing-docstring
        # Override the do_state_changed method that is automatically called
        # when the state-changed signal is emitted, and raises an exception.
        pass

    def _emit_position(self):
        """Emit a position-changed signal. Called every 200ms during
        playback."""
        position = self.get_position()
        duration = self.get_duration()
        if duration != 0:
            self.emit('position-changed', position, duration)

        return True

    def get_duration(self):
        """Return the duration of the file currently played, or 0 if it is
        unknown.

        This is not affected by the speed ratio."""
        success, duration = self.query_duration(Gst.Format.TIME)
        if success:
            return duration

        return 0

    def get_position(self):
        """Return the current playback position of the file, or 0 if it is
        unknown.

        This is not affected by the speed ratio."""
        success, position = self.playbin.query_position(Gst.Format.TIME)
        if success:
            return position

        return 0

    def _on_error(self, bus, message):
        """Called when there is an error during the playback."""
        self.set_state(Gst.State.NULL)
        err, debug = message.parse_error()
        print("Error: %s" % err, debug)

    def _on_eos(self, bus, message):
        """Called when the end of the audio file is reached."""
        duration = self.get_duration()
        self.emit('position-changed', duration, duration)
        self.set_state(Gst.State.READY)

    def _on_state_changed(self, bus, message):
        """Called when the state of an element of the pipeline changes."""
        state = message.parse_state_changed()[1]

        if message.src != self.playbin:
            # Ignore messages that do not come from the playbin
            return

        if state == Gst.State.READY:
            self._speed_set = False

        if state == Gst.State.PAUSED:
            self._emit_position()

        if state == Gst.State.PLAYING:
            if not self._speed_set:
                self._speed_set = True
                self.playbin.seek(
                    self._speed, Gst.Format.TIME, Gst.SeekFlags.FLUSH,
                    Gst.SeekType.SET, 0, Gst.SeekType.NONE, -1)

            if self.position_timer is None:
                self._emit_position()
                self.position_timer = (
                    GObject.timeout_add(100, self._emit_position)
                )
        else:
            if self.position_timer is not None:
                GObject.source_remove(self.position_timer)
                self.position_timer = None

        self.emit('state-changed', state)

    def seek(self, position):
        """Send a seek event to the playbin."""
        self.playbin.seek(self._speed, Gst.Format.TIME, Gst.SeekFlags.FLUSH,
                          Gst.SeekType.SET, position, Gst.SeekType.NONE, -1)

    def set_speed(self, speed):
        """Set the speed ratio."""
        if speed != self._speed:
            self._speed = speed

            position = self.get_position()
            self.playbin.seek(
                self._speed, Gst.Format.TIME, Gst.SeekFlags.FLUSH,
                Gst.SeekType.SET, position, Gst.SeekType.NONE, -1)

    def set_uri(self, uri):
        """Set the uri of the audio file."""
        self.set_state(Gst.State.NULL)
        self.playbin.set_property("uri", uri)
        self.set_state(Gst.State.PAUSED)

    def toggle(self):
        """Toggle between play and pause."""
        success, state, _ = self.get_state(0)
        if success != Gst.StateChangeReturn.SUCCESS:
            return

        if state == Gst.State.PLAYING:
            self.set_state(Gst.State.PAUSED)
        else:
            self.set_state(Gst.State.PLAYING)


class MainWindow(Gtk.Window):
    """The main window of audiotsmgtk."""
    def __init__(self):
        super().__init__(Gtk.WindowType.TOPLEVEL)
        self.set_title('audiotsmgtk')
        self.set_default_size(700, -1)
        self.connect('destroy', Gtk.main_quit)

        self._seeking = False

        # Headerbar
        headerbar = Gtk.HeaderBar()
        headerbar.set_title('audiotsmgtk')
        headerbar.set_show_close_button(True)
        self.set_titlebar(headerbar)

        # Open button
        icon_name = get_icon_name([
            'document-open-symbolic', 'document-open'])
        open_button = Gtk.Button.new_from_icon_name(
            icon_name, Gtk.IconSize.BUTTON)
        open_button.connect('clicked', self.on_open)
        headerbar.pack_start(open_button)

        # Play/pause button
        icon_name = get_icon_name([
            'media-playback-start-symbolic', 'media-playback-start'])
        self.toggle_button = Gtk.Button.new_from_icon_name(
            icon_name, Gtk.IconSize.BUTTON)
        self.toggle_button.connect('clicked', self.on_toggle)
        self.toggle_button.set_relief(Gtk.ReliefStyle.NONE)

        # Position and duration labels
        self.position_label = Gtk.Label("0:00")
        self.duration_label = Gtk.Label("0:00")

        # Seek bar
        self.seek_bar = Gtk.HScale.new_with_range(0, 100, 1)
        self.seek_bar.set_draw_value(False)
        self.seek_bar.connect('button-press-event', self.on_seeking_start)
        self.seek_bar.connect('button-release-event', self.on_seeking_end)

        # Speed
        speed_label = Gtk.Label.new("Speed:")
        speed_scale = Gtk.HScale.new_with_range(0, 100, 1)
        speed_scale.set_draw_value(False)
        for i in range(9):
            # Divide the speed scale in eight sections. Going from one marker
            # to the next will multiply the speed by two.
            speed_scale.add_mark(i * 12.5, Gtk.PositionType.BOTTOM, None)
        self.speed_label = Gtk.Label()
        speed_scale.connect('change-value', self.on_speed_scale_changed)
        speed_scale.connect('button-release-event',
                            self.on_speed_scale_released)
        speed_scale.set_value(50)
        self.speed_label.set_text('100.0 %')

        # Layout
        self.set_border_width(10)
        vbox = Gtk.VBox.new(False, 10)
        player_hbox = Gtk.HBox.new(False, 10)
        speed_hbox = Gtk.HBox.new(False, 10)

        player_hbox.pack_start(self.toggle_button, False, False, 0)
        player_hbox.pack_start(self.position_label, False, False, 0)
        player_hbox.pack_start(self.seek_bar, True, True, 0)
        player_hbox.pack_start(self.duration_label, False, False, 0)

        speed_hbox.pack_start(speed_label, False, False, 0)
        speed_hbox.pack_start(speed_scale, True, True, 0)
        speed_hbox.pack_start(self.speed_label, False, False, 0)

        vbox.pack_start(player_hbox, False, False, 0)
        vbox.pack_start(speed_hbox, False, False, 0)
        self.add(vbox)

        # Player
        self.player = Player()
        self.player.connect('position-changed', self.on_position_changed)
        self.player.connect('state-changed', self.on_state_changed)

    def open_file(self, path):
        """Open an audio file."""
        name = os.path.basename(path)
        self.set_title(name)

        uri = 'file://' + os.path.realpath(path)
        self.player.set_uri(uri)

    def on_open(self, button):
        """Called when the open button is clicked."""
        dialog = Gtk.FileChooserDialog(
            'Open audio file', self, Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            path = dialog.get_filename()
            self.open_file(path)

        dialog.destroy()

    def on_position_changed(self, player, position, duration):
        """Show the current playback position."""
        self.position_label.set_text(format_time(position))
        self.duration_label.set_text(format_time(duration))

        self.seek_bar.set_range(0, duration)
        if not self._seeking:
            self.seek_bar.set_value(position)

    def on_state_changed(self, player, state):
        """Show the state of the player."""
        if state == Gst.State.PLAYING:
            icon_name = get_icon_name([
                'media-playback-pause-symbolic', 'media-playback-pause'])
        else:
            icon_name = get_icon_name([
                'media-playback-start-symbolic', 'media-playback-start'])

        self.toggle_button.set_image(Gtk.Image.new_from_icon_name(
            icon_name, Gtk.IconSize.BUTTON))

    def on_seeking_start(self, seek_bar, event):
        """Called when the user clicks on the seek bar."""
        if event.button == 1:
            self._seeking = True

    def on_seeking_end(self, seek_bar, event):
        """Called when the user release the seek bar."""
        if event.button == 1:
            self._seeking = False
            self.player.seek(seek_bar.get_value())

    def on_speed_scale_changed(self, scale, scroll, value):
        """Called when the user changes the value of the speed scale."""
        # The value in the parameters may be bigger than the maximum value of
        # the scale. Overwrite it with the actual value of the scale.
        value = scale.get_value()

        # Convert the value of the scale to a speed. This makes the scale
        # logarithmic (adding 12.5 to the value of the scale multiplies the
        # speed by two).
        speed = 6.25 * np.exp(np.log(2) * value / 12.5)

        self.speed_label.set_text('{:.1f} %'.format(speed))

    def on_speed_scale_released(self, scale, event):
        """Called when the user releases the speed scale."""
        # The value in the parameters may be bigger than the maximum value of
        # the scale. Overwrite it with the actual value of the scale.
        value = scale.get_value()

        # Convert the value of the scale to a speed. This makes the scale
        # logarithmic (adding 12.5 to the value of the scale multiplies the
        # speed by two).
        speed = 6.25 * np.exp(np.log(2) * value / 12.5)

        self.speed_label.set_text('{:.1f} %'.format(speed))
        self.player.set_speed(speed / 100)

    def on_toggle(self, _):
        """Method called when the play/pause button is clicked."""
        self.player.toggle()


def main():
    """Run audiotsmgtk."""
    if len(sys.argv) <= 1:
        print('usage: audiotsmgtk.py <filename>')
        return

    Gst.init(sys.argv)

    window = MainWindow()
    window.open_file(sys.argv[1])

    window.show_all()

    GObject.threads_init()
    Gtk.main()


if __name__ == "__main__":
    main()
