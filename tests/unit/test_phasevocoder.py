# -*- coding: utf-8 -*-

"""
Tests for the audiotsm.phasevocoder package.
"""

import pytest
import numpy as np
from numpy.testing import assert_array_equal

from audiotsm.phasevocoder import find_peaks, get_closest_peaks


@pytest.mark.parametrize("amplitude, peaks", [
    ([], []),
    ([0], [True]),
    ([1], [True]),
    ([1, 0, 0, 1, 0, 0, 0, 1, 0],
     [True, False, False, True, False, False, False, True, False]),
    ([0, 1, 2, 3, 1, 2, 4, 5, -1, 6, 0],
     [False, False, False, True, False, False, False, False, False, True,
      False]),
])
def test_find_peaks(amplitude, peaks):
    """Run tests for the find_peaks function."""
    actual_peaks = find_peaks(np.array(amplitude))
    assert_array_equal(actual_peaks, np.array(peaks, dtype=bool))


@pytest.mark.parametrize("peaks, closest_peak", [
    ([], []),
    ([True], [0]),
    ([True], [0]),
    ([True, False, False, True, False, False, False, True, False],
     [0, 0, 3, 3, 3, 3, 7, 7, 7]),
    ([True, True, True, True, True, True, True, True, True],
     [0, 1, 2, 3, 4, 5, 6, 7, 8]),
    ([False, False, False, True, False, False, False, False, False, True,
      False],
     [3, 3, 3, 3, 3, 3, 3, 9, 9, 9, 9]),
])
def test_get_closest_peaks(peaks, closest_peak):
    """Run tests for the get_closest_peaks."""
    actual_closest_peak = get_closest_peaks(np.array(peaks))
    assert_array_equal(actual_closest_peak, np.array(closest_peak, dtype=int))
