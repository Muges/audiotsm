# -*- coding: utf-8 -*-

"""
The :mod:`audiotsm` module provides several time-scale modification procedures:

- :func:`~audiotsm.ola` (Overlap-Add), which should only be used for percussive
  audio signals;
- :func:`~audiotsm.wsola` (Waveform Similarity-based Overlap-Add), which should
  give good results on most inputs.

.. note::

    If you are not sure which procedure and parameters to use, using
    :func:`~audiotsm.wsola` with the default parameters should work in most
    cases.

Each of the function of this module returns a :class:`~audiotsm.base.tsm.TSM`
object which implements a time-scale modification procedure.

.. autofunction:: audiotsm.ola
.. autofunction:: audiotsm.wsola
"""

__version__ = "0.1.1"


from .ola import ola
from .wsola import wsola
