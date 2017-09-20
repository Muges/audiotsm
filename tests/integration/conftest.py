# -*- coding: utf-8 -*-

"""
Pytest configuration
"""

import fnmatch
import os
import pytest


def pytest_namespace():
    """Set pytest global variables."""
    return {'DATA_DIR': os.path.join("tests", "integration", "data")}


def pytest_addoption(parser):
    """Add command line options to the pytest command."""
    parser.addoption(
        "--data-all", action="store_true", help="run on all data files")
    parser.addoption(
        "--data-save", action="store_true",
        help="save the output of the data tests to build/examples")


def get_data_files():
    """Recursively look for wav files in the DATA_DIR directory, and returns
    their paths."""
    # pylint: disable=no-member
    data_files = []
    for root, _, filenames in os.walk(pytest.DATA_DIR):
        for filename in fnmatch.filter(filenames, '*.wav'):
            data_files.append(os.path.join(root, filename))

    return data_files


def pytest_generate_tests(metafunc):
    """Generate tests for test_data.py."""
    if 'speed' in metafunc.fixturenames:
        metafunc.parametrize('speed', [0.5, 1 / 1.2, 1 / 1.8, 2])

    if 'tsm_name' in metafunc.fixturenames:
        metafunc.parametrize('tsm_name', ["ola", "wsola", "phasevocoder"])

    if 'save' in metafunc.fixturenames:
        metafunc.parametrize("save", [metafunc.config.getoption('data_save')])

    if 'data_file' in metafunc.fixturenames:
        data_files = get_data_files()
        if not metafunc.config.getoption('data_all'):
            # Only test with two files
            data_files = data_files[:2]
        metafunc.parametrize("data_file", data_files)
