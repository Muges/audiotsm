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

import ast
import re
from setuptools import setup, find_packages
from sphinx.setup_command import BuildDoc


_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('audiotsm/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name="audiotsm",
    version=version,
    description="A real-time audio time-scale modification library",
    long_description=__doc__,
    license="MIT",
    url="https://github.com/Muges/audiotsm",
    author="Muges",
    author_email="git@muges.fr",

    packages=find_packages(),

    install_requires=[
        "numpy",
    ],
    setup_requires=[
        "pytest-runner",
        "pytest-pylint",
        "pytest-flake8",
        "pytest-coverage",
    ],
    tests_require=[
        "pytest",
        "pylint",
        "flake8"
    ],

    cmdclass={
        'doc': BuildDoc
    },

    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Multimedia :: Sound/Audio"
    ]
)