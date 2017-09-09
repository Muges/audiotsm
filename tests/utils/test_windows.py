# -*- coding: utf-8 -*-

"""
Tests for the audiotsm.utils.windows package.
"""

import pytest
import numpy as np
from numpy.testing import assert_almost_equal

from audiotsm.utils import windows


@pytest.mark.parametrize("buffer, window, out", [
    ([[]], None, [[]]),
    ([[]], [], [[]]),
    ([[1, 2, 3], [4, 5, 6]], None, [[1, 2, 3], [4, 5, 6]]),
    ([[1, 2, 3], [4, 5, 6]], [1, 1, 1], [[1, 2, 3], [4, 5, 6]]),
    ([[1, 2, 3], [4, 5, 6]], [2, 0.5, 1], [[2, 1, 3], [8, 2.5, 6]]),
])
def test_apply(buffer, window, out):
    """Run tests for apply."""
    buffer = np.array(buffer, dtype=np.float32)
    windows.apply(buffer, window)
    assert_almost_equal(buffer, np.array(out))


@pytest.mark.parametrize("length, window", [
    (0, []),
    (1, [0.]),
    (3, [0, 0.75, 0.75]),
    (4, [0, 0.5, 1, 0.5]),
    (8, [0, 0.14644661, 0.5, 0.85355339, 1, 0.85355339, 0.5, 0.146446611]),
])
def test_hanning(length, window):
    """Run tests for hanning."""
    assert_almost_equal(windows.hanning(length), np.array(window))


@pytest.mark.parametrize("window1, window2, out", [
    (None, None, None),
    (None, [], []),
    (None, [1, 2], [1, 2]),
    ([], None, []),
    ([1, 2], None, [1, 2]),
    ([1, 2], [3, 4], [3, 8]),
])
def test_product(window1, window2, out):
    """Run tests for product."""
    if window1 is not None:
        window1 = np.array(window1)
    if window2 is not None:
        window2 = np.array(window2)

    if out is None:
        assert windows.product(window1, window2) is None
    else:
        assert_almost_equal(windows.product(window1, window2), np.array(out))
