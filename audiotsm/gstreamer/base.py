# -*- coding: utf-8 -*-

"""
The :mod:`~audiotsm.gstreamer.base` module provides a base class for gstreamer
plugin using :class:`~audiotsm.base.tsm.TSM` objects.
"""

import sys
import numpy as np
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstAudio', '1.0')

# pylint: disable=wrong-import-position
from gi.repository import GObject, GLib, Gst, GstAudio
from audiotsm import __version__
from audiotsm.io.array import ArrayReader, ArrayWriter
from gstbasetransform import BaseTransform
# pylint: enable=wrong-import-position

Gst.init(sys.argv)

CAPS = Gst.Caps.from_string(
    "audio/x-raw,format=S16LE,layout=interleaved")


def audioformatinfo_to_dtype(info):
    """Return the data type corresponding to a ``GstAudio.AudioFormatInfo``
    object.

    :param info: a ``GstAudio.AudioFormatInfo``.
    :returns: the corresponding data type, to be used in :mod:`numpy`
        functions.
    """
    endianness = '<' if info.endianness == GLib.LITTLE_ENDIAN else '>'

    if info.flags & GstAudio.AudioFormatFlags.INTEGER:
        if info.flags & GstAudio.AudioFormatFlags.SIGNED:
            _type = 'i'
        else:
            _type = 'u'
    elif info.flags & GstAudio.AudioFormatFlags.FLOAT:
        _type = 'f'
    else:
        raise ValueError(
            'unsupported audio format flags: {}'.format(info.flags))

    samplewidth = info.width // 8  # in bytes

    return '{}{}{}'.format(endianness, _type, samplewidth)


class GstTSM(BaseTransform):
    """Gstreamer TSM plugin.

    Subclasses should implement the :func:`~GstTSM.create_tsm` method and
    provide two class attributes:

    - ``__gstmetadata__ = (longname, classification, description, author)``.
      See the documentation of the gst_element_class_set_metadata_ function for
      more details.
    - ``plugin_name``, the name of the plugin.

    Calling the :func:`~GstTSM.register` class method on a subclass will
    register it, enabling you to instantiate an audio filter with
    ``Gst.ElementFactory.make(plugin_name)``.

    .. _gst_element_class_set_metadata:
        https://gstreamer.freedesktop.org/data/doc/gstreamer/head/gstreamer/html/GstElement.html#gst-element-class-set-metadata
    """  # noqa: E501
    # pylint: disable=no-member

    __gsttemplates__ = (Gst.PadTemplate.new("src",
                                            Gst.PadDirection.SRC,
                                            Gst.PadPresence.ALWAYS,
                                            CAPS),
                        Gst.PadTemplate.new("sink",
                                            Gst.PadDirection.SINK,
                                            Gst.PadPresence.ALWAYS,
                                            CAPS))

    def __init__(self):
        super().__init__()

        self._channels = 0
        self._samplerate = 0
        self._bps = 0  # bytes per sample
        self._dtype = ''
        self._audioformatinfo = None

        self._tsm = None
        self._position = 0

    @classmethod
    def plugin_init(cls, plugin):
        """Initialize the plugin."""
        plugin_type = GObject.type_register(cls)
        Gst.Element.register(plugin, cls.plugin_name, 0, plugin_type)
        return True

    @classmethod
    def register(cls):
        """Register the plugin.

        Register the plugin to make it possible to instantiate it with
        ``Gst.ElementFactory.make``."""
        Gst.Plugin.register_static(
            Gst.VERSION_MAJOR, Gst.VERSION_MINOR, cls.plugin_name,
            cls.get_metadata('description'), cls.plugin_init, __version__,
            'MIT/X11', 'audiotsm', 'audiotsm', '')

    def _gstbuffer_to_ndarray(self, gstbuffer):
        """Return the data contained in ``gstbuffer`` as a
        :class:`numpy.ndarray`.

        :param gstbuffer: a :class:`Gst.Buffer`.
        """
        _, mapinfo = gstbuffer.map(Gst.MapFlags.READ)
        data = mapinfo.data
        gstbuffer.unmap(mapinfo)

        data = np.frombuffer(data, self._dtype).astype(np.float32) / 32767
        data = data.reshape((-1, self._channels)).T

        return data

    def _ndarray_to_gstbuffer(self, gstbuffer, data):
        """Write the ``data`` to ``gstbuffer``.

        This method is a bit hack-ish. It would be better to set the size of
        the :class:`Gst.Buffer` in advance with the
        :func:`GstBase.BaseTransform.do_transform_size` virtual method, but it
        is not possible to do so with pygst.

        :param gstbuffer: a :class:`Gst.Buffer`.
        :param data: a :class:`numpy.ndarray`.
        """
        length = data.shape[1]

        if length <= 0:
            gstbuffer.set_size(0)
            gstbuffer.duration = 0
            return

        data = (data.T.reshape((-1,)) * 32767).astype(self._dtype).tobytes()
        size = len(data)

        # Copy as many bytes as possible to the buffer directly
        n = gstbuffer.fill(0, data)

        if n < size:
            Gst.warning('the output buffer is too small, allocating memory')

            # Allocate memory for the rest of the data
            # This may add noise to the audio signal
            data = data[n:]
            mem = Gst.Memory.new_wrapped(0, data, len(data), 0, None, None)
            gstbuffer.append_memory(mem)

        gstbuffer.set_size(size)

    def do_sink_event(self, event):
        """Sink pad event handler."""
        if event.type == Gst.EventType.CAPS:
            # CAPS event, used to negotiate the format with the "upstream"
            # gstreamer element.
            caps = event.parse_caps()
            structure = caps.get_structure(0)

            # Ensure that the layout is interleaved
            layout = structure.get_string('layout')
            if layout != 'interleaved':
                # Returns False if we were unable to agree on a format.
                return False

            # Get number of channels
            success, self._channels = structure.get_int('channels')
            if not success:
                # Returns False if we were unable to agree on a format.
                return False

            # Get samplerate
            success, self._samplerate = structure.get_int('rate')
            if not success:
                # Returns False if we were unable to agree on a format.
                return False

            # Get and parse samples format
            samples_format = structure.get_string('format')
            if samples_format is None:
                # Returns False if we were unable to agree on a format.
                return False

            self._audioformatinfo = GstAudio.AudioFormat.get_info(
                GstAudio.AudioFormat.from_string(samples_format)
            )
            self._dtype = audioformatinfo_to_dtype(self._audioformatinfo)

            self._bps = self._channels * self._audioformatinfo.width // 8

            # Create the TSM object
            self._tsm = self.create_tsm(self._channels)

        if event.type == Gst.EventType.SEGMENT:
            segment = event.parse_segment()

            self._tsm.set_speed(segment.rate)
            self._position = segment.position

            segment.applied_rate = segment.rate
            segment.rate = 1.0
            event = Gst.Event.new_segment(segment)
            self.srcpad.push_event(event)

        if event.type == Gst.EventType.EOS:
            # Flush the TSM object at the end of the stream
            writer = ArrayWriter(self._channels)
            self._tsm.flush_to(writer)

            # Write the output to a Gst.Buffer
            out_buffer = Gst.Buffer.new()
            self._ndarray_to_gstbuffer(out_buffer, writer.data)

            out_buffer.pts = self._position
            self._position += out_buffer.duration

            # Send the buffer downstream
            self.srcpad.push(out_buffer)

        # Propagate the event downstream
        return self.srcpad.push_event(event)

    def do_transform(self, in_buffer, out_buffer):
        """Run the data of ``in_buffer`` through the
        :class:`~audiotsm.base.tsm.TSM` object and write the output to
        ``out_buffer``.

        :param in_buffer: a ``Gst.Buffer`` containing the input data.
        :param out_buffer: a ``Gst.Buffer`` where the output data will be
            written.
        """
        # There is a bug that increases the refcount of out_buffer, making it
        # non writable (https://bugzilla.gnome.org/show_bug.cgi?id=727702#c4).
        # Set the refcount to 1 to fix this.
        refcount = out_buffer.mini_object.refcount
        out_buffer.mini_object.refcount = 1

        # Set the position of the output buffer
        out_buffer.pts = self._position

        # Run the TSM procedure
        reader = ArrayReader(self._gstbuffer_to_ndarray(in_buffer))
        writer = ArrayWriter(self._channels)

        self._tsm.run(reader, writer, flush=False)

        self._ndarray_to_gstbuffer(out_buffer, writer.data)
        out_buffer.duration = (
            (out_buffer.get_size() * Gst.SECOND) //
            (self._bps * self._samplerate)
        )
        self._position += out_buffer.duration

        # Reset the refcount
        out_buffer.mini_object.refcount = refcount

        return Gst.FlowReturn.OK

    def do_transform_size(self, direction, caps, size, othercaps):
        """Returns the size of the output buffer given the size of the input
        buffer."""
        input_length = size // self._bps
        output_length = self._tsm.get_max_output_length(input_length)
        output_size = output_length * self._bps
        return True, output_size

    def create_tsm(self, channels):
        """Returns the :class:`~audiotsm.base.tsm.TSM` object used by the audio
        filter."""
        raise NotImplementedError()
