# -*- coding: utf-8 -*-

"""
Tests for the audiotsm.windows package.
"""

import pytest
from pytest import approx

import numpy as np
from audiotsm.windows import hanning


@pytest.mark.parametrize("length, window", [
    (0, []),
    (1, [0.]),
    (3, [0, 0.75, 0.75]),
    (4, [0, 0.5, 1, 0.5]),
    (8, [0, 0.14644661, 0.5, 0.85355339, 1, 0.85355339, 0.5, 0.146446611]),
])
def test_hanning(length, window):
    """Run tests for hanning."""
    assert hanning(length) == approx(np.array(window))
