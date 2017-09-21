# -*- coding: utf-8 -*-

"""
The :mod:`audiotsm` module provides several time-scale modification procedures:

- :func:`~audiotsm.ola` (Overlap-Add);
- :func:`~audiotsm.wsola` (Waveform Similarity-based Overlap-Add);
- :func:`~audiotsm.phasevocoder` (Phase Vocoder).

The OLA procedure should only be used on percussive audio signals. The WSOLA
and the Phase Vocoder procedures are improvements of the OLA procedure, and
should both give good results in most cases.

.. note::

    If you are unsure which procedure and parameters to choose, using
    :func:`~audiotsm.phasevocoder` with the default parameters should give good
    results in most cases. You can listen to the output of the different
    procedures on various audio files and at various speeds on the `examples
    page`_.

Each of the function of this module returns a :class:`~audiotsm.base.tsm.TSM`
object which implements a time-scale modification procedure.

.. autofunction:: audiotsm.ola
.. autofunction:: audiotsm.wsola
.. autofunction:: audiotsm.phasevocoder

.. _examples page: https://muges.github.io/audiotsm/
"""

__version__ = "0.1.2"


from .ola import ola
from .wsola import wsola
from .phasevocoder import phasevocoder
