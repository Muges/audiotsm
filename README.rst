A real-time audio time-scale modification library
=================================================

AudioTSM is a python library for real-time audio time-scale modification
procedures, i.e. algorithms that change the speed of an audio signal without
changing its pitch.

Source code repository and issue tracker:
   http://github.com/Muges/audiotsm

License:
   MIT -- see the file ``LICENSE`` for details.

Installation
------------

For now you should probably install audiotsm directly from the github
repository using pip::

    pip install git+https://github.com/Muges/audiotsm.git

A package should be available on PyPI soon.


You may also need to install the sounddevice_ library in order to run the
examples or to use a ``StreamWriter``.

.. _sounddevice: http://github.com/spatialaudio/python-sounddevice/

Basic usage
-----------

The audiotsm package implements several time-scale modification procedures:

 - OLA (Overlap-Add), which should only be used for percussive audio signals;
 - WSOLA (Waveform Similarity-based Overlap-Add), an amelioration of the OLA
   procedure which should give good results on most inputs.

Below is a basic example showing how to reduce the speed of a wav file by half
using the WSOLA procedure::

    from audiotsm import wsola
    from audiotsm.io.wav import WavReader, WavWriter

    with WavReader(input_filename) as reader:
        with WavWriter(output_filename, reader.channels, reader.samplerate) as writer:
            tsm = wsola(reader.channels, speed=0.5)
            tsm.run(reader, writer)

Thanks
------

If you are interested in time-scale modification procedures, I highly recommend
reading `A Review of Time-Scale Modification of Music Signals`_ by Jonathan
Driedger and Meinard Müller.

.. _A Review of Time-Scale Modification of Music Signals:
    http://www.mdpi.com/2076-3417/6/2/57
