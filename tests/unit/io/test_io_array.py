# -*- coding: utf-8 -*-

"""
Tests for the audiotsm.io.array package.
"""

import pytest
import numpy as np
from numpy.testing import assert_almost_equal

from audiotsm.io.array import ArrayReader, ArrayWriter, FixedArrayWriter


@pytest.mark.parametrize("data_in, read_out, n_out, data_out", [
    ([[]], [[]], 0, [[]]),
    ([[]], [[0]], 0, [[]]),
    ([[1, 2, 3], [4, 5, 6]], [[], []], 0, [[1, 2, 3], [4, 5, 6]]),
    ([[1, 2, 3], [4, 5, 6]], [[1], [4]], 1, [[2, 3], [5, 6]]),
    ([[1, 2, 3], [4, 5, 6]], [[1, 2], [4, 5]], 2, [[3], [6]]),
    ([[1, 2, 3], [4, 5, 6]], [[1, 2, 3], [4, 5, 6]], 3, [[], []]),
    ([[1, 2, 3], [4, 5, 6]], [[1, 2, 3, 0], [4, 5, 6, 0]], 3, [[], []]),
])
def test_read(data_in, read_out, n_out, data_out):
    """Run tests for the ArrayReader.read method."""
    reader = ArrayReader(np.array(data_in))

    buffer = np.zeros_like(read_out, dtype=np.float32)
    n = reader.read(buffer)
    assert_almost_equal(buffer, read_out)
    assert n == n_out

    # Check the data remaining in the reader
    buffer = np.zeros_like(data_out)
    reader.read(buffer)
    assert_almost_equal(buffer, data_out)

    # Check that there is no more data in the reader
    buffer = np.zeros_like(data_in)
    n = reader.read(buffer)
    assert not buffer.any()
    assert n == 0


@pytest.mark.parametrize("data_in, n_in, n_out, data_out", [
    ([[]], 0, 0, [[]]),
    ([[]], 1, 0, [[]]),
    ([[1, 2, 3], [4, 5, 6]], 0, 0, [[1, 2, 3], [4, 5, 6]]),
    ([[1, 2, 3], [4, 5, 6]], 1, 1, [[2, 3], [5, 6]]),
    ([[1, 2, 3], [4, 5, 6]], 2, 2, [[3], [6]]),
    ([[1, 2, 3], [4, 5, 6]], 3, 3, [[], []]),
    ([[1, 2, 3], [4, 5, 6]], 4, 3, [[], []]),
])
def test_skip(data_in, n_in, n_out, data_out):
    """Run tests for the ArrayReader.skip method."""
    reader = ArrayReader(np.array(data_in))

    n = reader.skip(n_in)
    assert n == n_out

    # Check the data remaining in the reader
    buffer = np.zeros_like(data_out)
    reader.read(buffer)
    assert_almost_equal(buffer, data_out)

    # Check that there is no more data in the reader
    buffer = np.zeros_like(data_in)
    n = reader.read(buffer)
    assert not buffer.any()
    assert n == 0


@pytest.mark.parametrize("write1, write2, n1_out, n2_out, buffer_out", [
    ([[], []], [[], []], 0, 0, [[], []]),

    ([[1, 2, 3], [4, 5, 6]], [[], []], 3, 0, [[1, 2, 3], [4, 5, 6]]),
    ([[1, 2], [4, 5]], [[3], [6]], 2, 1, [[1, 2, 3], [4, 5, 6]]),
    ([[1], [4]], [[2, 3], [5, 6]], 1, 2, [[1, 2, 3], [4, 5, 6]]),
    ([[], []], [[1, 2, 3], [4, 5, 6]], 0, 3, [[1, 2, 3], [4, 5, 6]]),

    ([[1, 2, 3], [4, 5, 6]], [[7], [8]], 3, 0, [[1, 2, 3], [4, 5, 6]]),
    ([[1, 2, 3], [4, 5, 6]], [[7], [8]], 2, 0, [[1, 2], [4, 5]]),

    ([[1, 2], [4, 5]], [[], []], 2, 0, [[1, 2, 0], [4, 5, 0]]),
])
def test_fixed_array_write(write1, write2, n1_out, n2_out, buffer_out):
    """Run tests for the FixedArrayWriter.write method."""
    buffer = np.zeros_like(buffer_out, dtype=np.float32)
    writer = FixedArrayWriter(buffer)

    n = writer.write(np.array(write1, dtype=np.float32))
    assert n == n1_out
    n = writer.write(np.array(write2, dtype=np.float32))
    assert n == n2_out

    assert_almost_equal(buffer, buffer_out)


@pytest.mark.parametrize("write1, write2, n1_out, n2_out, buffer_out", [
    ([[], []], [[], []], 0, 0, [[], []]),

    ([[1, 2, 3], [4, 5, 6]], [[], []], 3, 0, [[1, 2, 3], [4, 5, 6]]),
    ([[1, 2], [4, 5]], [[3], [6]], 2, 1, [[1, 2, 3], [4, 5, 6]]),
    ([[1], [4]], [[2, 3], [5, 6]], 1, 2, [[1, 2, 3], [4, 5, 6]]),
    ([[], []], [[1, 2, 3], [4, 5, 6]], 0, 3, [[1, 2, 3], [4, 5, 6]]),

    ([[1, 2], [4, 5]], [[], []], 2, 0, [[1, 2], [4, 5]]),
])
def test_array_write(write1, write2, n1_out, n2_out, buffer_out):
    """Run tests for the ArrayWriter.write method."""
    writer = ArrayWriter(len(write1))

    n = writer.write(np.array(write1, dtype=np.float32))
    assert n == n1_out
    n = writer.write(np.array(write2, dtype=np.float32))
    assert n == n2_out

    assert_almost_equal(writer.data, buffer_out)
