# -*- coding: utf-8 -*-

"""
The :mod:`audiotsm.gstreamer` module implements audio filters allowing to use
the TSM procedures with gstreamer.

In order to use these audio filters, you should first import the module
corresponding to the TSM procedure you want to use, for example::

    import audiotsm.gstreamer.wsola

Then, you should create the audio filter with ``Gst.ElementFactory.make``, as
follow::

    tsm = Gst.ElementFactory.make("audiotsm-wsola")

You should then create a gstreamer pipeline using the audio filter you created.
See ``examples/audiotsmgtk_basic.py`` for an example of pipeline.
"""
