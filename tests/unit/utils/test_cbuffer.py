# -*- coding: utf-8 -*-

"""
Tests for the audiotsm.utils.cbuffer package.
"""

import pytest
import numpy as np
from numpy.testing import assert_almost_equal

from audiotsm.io.array import ArrayReader, FixedArrayWriter
from audiotsm.utils import CBuffer


def generate_cbuffers(array, ready, max_length):
    """Generate different CBuffers containing the same data as ``array``."""
    array = np.array(array)
    for i in range(0, max_length):
        buffer = CBuffer(array.shape[0], max_length)

        # Add and remove i samples to rotate the buffer
        buffer.right_pad(i)
        buffer.remove(i)

        buffer.right_pad(array.shape[1])
        buffer.add(array)
        buffer.set_ready(ready)
        yield buffer


def generate_test_cases(cases):
    """For each tuple (data, ready, max_length, *params) of an array, generate
    multiple test cases (buffer, *params), where buffer is a CBuffer containing
    ``data``."""
    for case in cases:
        for buffer in generate_cbuffers(*case[:3]):
            yield (buffer,) + case[3:]


@pytest.mark.parametrize("in_buffer, add, out", generate_test_cases([
    ([[]], 0, 0, [[]], [[]]),
    ([[]], 0, 2, [[]], [[]]),
    ([[1, 2, 3], [4, 5, 6]], 3, 3, [[], []], [[1, 2, 3], [4, 5, 6]]),
    ([[1, 2, 3], [4, 5, 6]], 3, 5, [[], []], [[1, 2, 3], [4, 5, 6]]),
    ([[1, 2, 3], [4, 5, 6]], 3, 3, [[0.25, -0.25], [0.5, -0.5]],
     [[1.25, 1.75, 3], [4.5, 4.5, 6]]),
    ([[1, 2, 3], [4, 5, 6]], 3, 5, [[0.25, -0.25], [0.5, -0.5]],
     [[1.25, 1.75, 3], [4.5, 4.5, 6]]),
    ([[1, 2, 3], [4, 5, 6]], 3, 3, [[0.25, 0, -0.25], [0.5, 0, -0.5]],
     [[1.25, 2, 2.75], [4.5, 5, 5.5]]),
    ([[1, 2, 3], [4, 5, 6]], 3, 5, [[0.25, 0, -0.25], [0.5, 0, -0.5]],
     [[1.25, 2, 2.75], [4.5, 5, 5.5]]),
]))
def test_cbuffer_add(in_buffer, add, out):
    """Run tests for the CBuffer.add method."""
    in_buffer.add(np.array(add))
    assert_almost_equal(in_buffer.to_array(), np.array(out))


@pytest.mark.parametrize("in_buffer, array, out", generate_test_cases([
    ([[]], 0, 0, [], [[]]),
    ([[]], 0, 2, [], [[]]),
    ([[1, 2, 3], [4, 5, 6]], 3, 3, [], [[1, 2, 3], [4, 5, 6]]),
    ([[1, 2, 3], [4, 5, 6]], 3, 5, [], [[1, 2, 3], [4, 5, 6]]),
    ([[1, 2, 3], [4, 5, 6]], 3, 3, [0.5], [[2, 2, 3], [8, 5, 6]]),
    ([[1, 2, 3], [4, 5, 6]], 3, 3, [0.5, 0.25], [[2, 8, 3], [8, 20, 6]]),
    ([[1, 2, 3], [4, 5, 6]], 3, 3, [0.5, 0.25, 3], [[2, 8, 1], [8, 20, 2]]),
    ([[1, 2, 3], [4, 5, 6]], 3, 5, [0.5], [[2, 2, 3], [8, 5, 6]]),
    ([[1, 2, 3], [4, 5, 6]], 3, 5, [0.5, 0.25], [[2, 8, 3], [8, 20, 6]]),
    ([[1, 2, 3], [4, 5, 6]], 3, 5, [0.5, 0.25, 3], [[2, 8, 1], [8, 20, 2]]),
]))
def test_cbuffer_divide(in_buffer, array, out):
    """Run tests for the CBuffer.divide method."""
    in_buffer.divide(np.array(array))
    assert_almost_equal(in_buffer.to_array(), np.array(out))


@pytest.mark.parametrize(
    "in_buffer, out_buffer, out_n, remaining_data",
    generate_test_cases([
        ([[]], 0, 0, [[]], 0, [[]]),
        ([[]], 0, 2, [[]], 0, [[]]),
        ([[]], 0, 0, [[0, 0]], 0, [[]]),
        ([[]], 0, 2, [[0, 0]], 0, [[]]),

        ([[1, 2, 3], [4, 5, 6]], 3, 3, [[], []], 0, [[1, 2, 3], [4, 5, 6]]),
        ([[1, 2, 3], [4, 5, 6]], 3, 3, [[1], [4]], 1, [[2, 3], [5, 6]]),
        ([[1, 2, 3], [4, 5, 6]], 3, 3, [[1, 2], [4, 5]], 2, [[3], [6]]),
        ([[1, 2, 3], [4, 5, 6]], 3, 3, [[1, 2, 3], [4, 5, 6]], 3, [[], []]),
        ([[1, 2, 3], [4, 5, 6]], 3, 3, [[1, 2, 3, 0], [4, 5, 6, 0]], 3,
         [[], []]),

        ([[1, 2, 3], [4, 5, 6]], 3, 5, [[], []], 0, [[1, 2, 3], [4, 5, 6]]),
        ([[1, 2, 3], [4, 5, 6]], 3, 5, [[1], [4]], 1, [[2, 3], [5, 6]]),
        ([[1, 2, 3], [4, 5, 6]], 3, 5, [[1, 2], [4, 5]], 2, [[3], [6]]),
        ([[1, 2, 3], [4, 5, 6]], 3, 5, [[1, 2, 3], [4, 5, 6]], 3, [[], []]),
        ([[1, 2, 3], [4, 5, 6]], 3, 5, [[1, 2, 3, 0], [4, 5, 6, 0]], 3,
         [[], []]),

        ([[1, 2, 3], [4, 5, 6]], 2, 3, [[], []], 0, [[1, 2], [4, 5]]),
        ([[1, 2, 3], [4, 5, 6]], 2, 3, [[1], [4]], 1, [[2], [5]]),
        ([[1, 2, 3], [4, 5, 6]], 2, 3, [[1, 2], [4, 5]], 2, [[], []]),
        ([[1, 2, 3], [4, 5, 6]], 2, 3, [[1, 2, 0], [4, 5, 0]], 2, [[], []]),
        ([[1, 2, 3], [4, 5, 6]], 2, 3, [[1, 2, 0, 0], [4, 5, 0, 0]], 2,
         [[], []]),
    ]))
def test_cbuffer_read(in_buffer, out_buffer, out_n, remaining_data):
    """Run tests for the CBuffer.read method."""
    read_buffer = np.zeros_like(out_buffer, dtype=np.float32)
    n = in_buffer.read(read_buffer)

    assert n == out_n
    assert_almost_equal(read_buffer, out_buffer)
    assert_almost_equal(in_buffer.to_array(), remaining_data)


@pytest.mark.parametrize(
    "in_buffer, write_buffer, out_n, out_data",
    generate_test_cases([
        ([[]], 0, 0, [[]], 0, [[]]),
        ([[], []], 0, 0, [[], []], 0, [[], []]),
        ([[], []], 0, 0, [[1, 2], [3, 4]], 0, [[], []]),
        ([[], []], 0, 1, [[1, 2], [3, 4]], 1, [[1], [3]]),
        ([[], []], 0, 2, [[1, 2], [3, 4]], 2, [[1, 2], [3, 4]]),
        ([[1, 2, 3], [4, 5, 6]], 3, 3, [[7, 8], [9, 0]], 0,
         [[1, 2, 3], [4, 5, 6]]),
        ([[1, 2, 3], [4, 5, 6]], 3, 4, [[7, 8], [9, 0]], 1,
         [[1, 2, 3, 7], [4, 5, 6, 9]]),
        ([[1, 2, 3], [4, 5, 6]], 3, 5, [[7, 8], [9, 0]], 2,
         [[1, 2, 3, 7, 8], [4, 5, 6, 9, 0]]),
    ]))
def test_cbuffer_read_from(in_buffer, write_buffer, out_n, out_data):
    """Run tests for the CBuffer.write method."""
    reader = ArrayReader(np.array(write_buffer))
    n = in_buffer.read_from(reader)

    assert n == out_n
    assert_almost_equal(in_buffer.to_array(), out_data)


@pytest.mark.parametrize(
    "in_buffer, write_buffer, out_n, out_data",
    generate_test_cases([
        ([[]], 0, 0, [[]], 0, [[]]),
        ([[], []], 0, 0, [[], []], 0, [[], []]),
        ([[], []], 0, 0, [[1, 2], [3, 4]], 0, [[], []]),
        ([[], []], 0, 1, [[1, 2], [3, 4]], 1, [[1], [3]]),
        ([[], []], 0, 2, [[1, 2], [3, 4]], 2, [[1, 2], [3, 4]]),
        ([[1, 2, 3], [4, 5, 6]], 3, 3, [[7, 8], [9, 0]], 0,
         [[1, 2, 3], [4, 5, 6]]),
        ([[1, 2, 3], [4, 5, 6]], 3, 4, [[7, 8], [9, 0]], 1,
         [[1, 2, 3, 7], [4, 5, 6, 9]]),
        ([[1, 2, 3], [4, 5, 6]], 3, 5, [[7, 8], [9, 0]], 2,
         [[1, 2, 3, 7, 8], [4, 5, 6, 9, 0]]),
    ]))
def test_cbuffer_write(in_buffer, write_buffer, out_n, out_data):
    """Run tests for the CBuffer.write method."""
    n = in_buffer.write(np.array(write_buffer))

    assert n == out_n
    assert_almost_equal(in_buffer.to_array(), out_data)


@pytest.mark.parametrize(
    "in_buffer, out_buffer, out_n, remaining_data",
    generate_test_cases([
        ([[]], 0, 0, [[]], 0, [[]]),
        ([[]], 0, 2, [[]], 0, [[]]),
        ([[]], 0, 0, [[0, 0]], 0, [[]]),
        ([[]], 0, 2, [[0, 0]], 0, [[]]),

        ([[1, 2, 3], [4, 5, 6]], 3, 3, [[], []], 0, [[1, 2, 3], [4, 5, 6]]),
        ([[1, 2, 3], [4, 5, 6]], 3, 3, [[1], [4]], 1, [[2, 3], [5, 6]]),
        ([[1, 2, 3], [4, 5, 6]], 3, 3, [[1, 2], [4, 5]], 2, [[3], [6]]),
        ([[1, 2, 3], [4, 5, 6]], 3, 3, [[1, 2, 3], [4, 5, 6]], 3, [[], []]),
        ([[1, 2, 3], [4, 5, 6]], 3, 3, [[1, 2, 3, 0], [4, 5, 6, 0]], 3,
         [[], []]),

        ([[1, 2, 3], [4, 5, 6]], 3, 5, [[], []], 0, [[1, 2, 3], [4, 5, 6]]),
        ([[1, 2, 3], [4, 5, 6]], 3, 5, [[1], [4]], 1, [[2, 3], [5, 6]]),
        ([[1, 2, 3], [4, 5, 6]], 3, 5, [[1, 2], [4, 5]], 2, [[3], [6]]),
        ([[1, 2, 3], [4, 5, 6]], 3, 5, [[1, 2, 3], [4, 5, 6]], 3, [[], []]),
        ([[1, 2, 3], [4, 5, 6]], 3, 5, [[1, 2, 3, 0], [4, 5, 6, 0]], 3,
         [[], []]),

        ([[1, 2, 3], [4, 5, 6]], 2, 3, [[], []], 0, [[1, 2], [4, 5]]),
        ([[1, 2, 3], [4, 5, 6]], 2, 3, [[1], [4]], 1, [[2], [5]]),
        ([[1, 2, 3], [4, 5, 6]], 2, 3, [[1, 2], [4, 5]], 2, [[], []]),
        ([[1, 2, 3], [4, 5, 6]], 2, 3, [[1, 2, 0], [4, 5, 0]], 2, [[], []]),
        ([[1, 2, 3], [4, 5, 6]], 2, 3, [[1, 2, 0, 0], [4, 5, 0, 0]], 2,
         [[], []]),
    ]))
def test_cbuffer_write_to(in_buffer, out_buffer, out_n, remaining_data):
    """Run tests for the CBuffer.read method."""
    read_buffer = np.zeros_like(out_buffer, dtype=np.float32)
    writer = FixedArrayWriter(read_buffer)
    n = in_buffer.write_to(writer)

    assert n == out_n
    assert_almost_equal(read_buffer, out_buffer)
    assert_almost_equal(in_buffer.to_array(), remaining_data)
