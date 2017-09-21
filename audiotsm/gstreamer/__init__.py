# -*- coding: utf-8 -*-

"""
The :mod:`audiotsm.gstreamer` module implements three audio filters allowing to
use the TSM procedures with gstreamer:

- ``audiotsm-ola``, defined in the :mod:`audiotsm.gstreamer.ola` module;
- ``audiotsm-wsola``, defined in the :mod:`audiotsm.gstreamer.wsola` module;
- ``audiotsm-phase-vocoder``, defined in the
  :mod:`audiotsm.gstreamer.phasevocoder` module.

.. note::

    If you are unsure which filter to choose, using ``audiotsm-phase-vocoder``
    should give good results in most cases. You can listen to the output of the
    different procedures on various audio files and at various speeds on the
    `examples page`_.

In order to use these audio filters, you should first import the module
corresponding to the TSM procedure you want to use, for example::

    import audiotsm.gstreamer.phasevocoder

Then, you should create the audio filter with ``Gst.ElementFactory.make``, as
follow::

    tsm = Gst.ElementFactory.make("audiotsm-phase-vocoder")

You should then create a gstreamer pipeline using the audio filter you created.
See ``examples/audiotsmcli_gst.py`` for an example of pipeline.

The audio filters work in the same manner as the ``scaletempo`` gstreamer
plugin. You can change the playback rate by sending a seek event to the
pipeline::

    speed = 0.5
    pipeline.seek(speed, Gst.Format.BYTES, Gst.SeekFlags.FLUSH,
                  Gst.SeekType.NONE, -1, Gst.SeekType.NONE, -1)

The other parameters of the TSM procedure are available as properties, as
documented for each of the procedures below.

.. _examples page: https://muges.github.io/audiotsm/
"""
