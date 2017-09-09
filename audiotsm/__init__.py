# -*- coding: utf-8 -*-

"""
AudioTSM
~~~~~~~~

AudioTSM is a python library for real-time audio time-scale modification
procedures, i.e. algorithms that change the speed of an audio signal without
changing its pitch.

:copyright: (c) 2017 by Muges.
:license: MIT, see LICENSE for more details.
"""

__version__ = "0.1.0"


from .ola import ola
from .wsola import wsola
