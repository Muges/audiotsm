# -*- coding: utf-8 -*-

"""
A real-time audio time-scale modification library
=================================================

AudioTSM is a python library for real-time audio time-scale modification
procedures, i.e. algorithms that change the speed of an audio signal without
changing its pitch.

Source code repository and issue tracker:
   http://github.com/Muges/audiotsm

License:
   MIT -- see the file ``LICENSE`` for details.
"""

__version__ = "0.1.0"


from .ola import ola
from .wsola import wsola
