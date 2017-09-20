#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=invalid-name
"""
AudioTSM
~~~~~~~~

AudioTSM is a python library for real-time audio time-scale modification
procedures, i.e. algorithms that change the speed of an audio signal without
changing its pitch.

:copyright: (c) 2017 by Muges.
:license: MIT, see LICENSE for more details.
"""

import os
import re
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


def find_version():
    """Read the package's version from __init__.py"""
    version_filename = os.path.abspath("audiotsm/__init__.py")
    with open(version_filename) as fileobj:
        version_content = fileobj.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_content, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--cov=audiotsm', 'tests/unit']
        self.test_suite = True

    def run_tests(self):
        import pytest

        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


# 'setup.py publish' shortcut.
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel')
    os.system('twine upload dist/*')
    sys.exit()


with open('README.rst', 'r') as f:
    long_description = f.read()


setup(
    name="audiotsm",
    version=find_version(),
    description="A real-time audio time-scale modification library",
    long_description=long_description,
    license="MIT",
    url="https://github.com/Muges/audiotsm",
    author="Muges",
    author_email="git@muges.fr",

    packages=find_packages(),

    install_requires=[
        "numpy",
    ],
    tests_require=[
        "pytest",
        "pytest-coverage",
        "sounddevice",
    ],
    extras_require={
        "stream": ["sounddevice"],
        "gstreamer": ["gstbasetransform"]
    },

    cmdclass={
        'test': PyTest,
    },

    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Multimedia :: Sound/Audio"
    ]
)
