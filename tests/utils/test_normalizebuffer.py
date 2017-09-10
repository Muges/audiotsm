# -*- coding: utf-8 -*-

"""
Tests for the audiotsm.utils.normalizebuffer package.
"""

import pytest
from numpy.testing import assert_almost_equal

from audiotsm.utils import NormalizeBuffer


def generate_normalize_buffers(array):
    """Generate different NormalizeBuffers containing the same data as
    ``array``."""
    for i in range(0, len(array)):
        buffer = NormalizeBuffer(len(array))
        buffer.remove(i)
        buffer.add(array)
        yield buffer


def generate_test_cases(cases):
    """For each tuple (data, *params) of an array, generate multiple test cases
    (buffer, *params), where buffer is a NormalizeBuffer containing
    ``data``."""
    for case in cases:
        for buffer in generate_normalize_buffers(case[0]):
            yield (buffer,) + case[1:]


@pytest.mark.parametrize("buffer, window, out", generate_test_cases([
    ([], [], []),
    ([0.5, 1.5, 2.5], [0.25, 0, -0.25], [0.75, 1.5, 2.25]),
    ([0.5, 1.5, 2.5, 3.5, 4.5], [0.25, 0, -0.25], [0.75, 1.5, 2.25, 3.5, 4.5])
]))
def test_normalize_buffer_add(buffer, window, out):
    """Run tests for the NormalizeBuffer.add method."""
    buffer.add(window)
    assert_almost_equal(buffer.to_array(), out)


@pytest.mark.parametrize("buffer, n, out", generate_test_cases([
    ([], 0, []),
    ([1], 0, [1]),
    ([1], 1, [0]),
    ([1, 0.75, 0.5], 0, [1, 0.75, 0.5]),
    ([1, 0.75, 0.5], 1, [0.75, 0.5, 0]),
    ([1, 0.75, 0.5], 2, [0.5, 0, 0]),
    ([1, 0.75, 0.5], 3, [0, 0, 0]),
    ([1, 0.75, 0.5], 4, [0, 0, 0]),
]))
def test_normalize_buffer_remove(buffer, n, out):
    """Run tests for the NormalizeBuffer.remove method."""
    buffer.remove(n)
    assert_almost_equal(buffer.to_array(), out)


@pytest.mark.parametrize("buffer, start, end, out", generate_test_cases([
    ([], 0, 0, []),
    ([1], 0, 0, []),
    ([1], 0, 1, [1]),
    ([1, 0.75, 0.5], 0, 0, []),
    ([1, 0.75, 0.5], 0, 1, [1]),
    ([1, 0.75, 0.5], 0, 2, [1, 0.75]),
    ([1, 0.75, 0.5], 0, 3, [1, 0.75, 0.5]),
    ([1, 0.75, 0.5], 1, 1, []),
    ([1, 0.75, 0.5], 1, 2, [0.75]),
    ([1, 0.75, 0.5], 1, 3, [0.75, 0.5]),
    ([1, 0.75, 0.5], 2, 2, []),
    ([1, 0.75, 0.5], 2, 3, [0.5]),
    ([1, 0.75, 0.5], 3, 3, []),
]))
def test_normalize_buffer_to_array(buffer, start, end, out):
    """Run tests for the NormalizeBuffer.to_array method."""
    assert_almost_equal(buffer.to_array(start, end), out)
