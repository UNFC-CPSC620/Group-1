"""
TASK-07: Infinite Price Validation Tests

Verify that analyze_prices_by_room_type() excludes infinite
and invalid prices from Airbnb room type statistics.

These tests address the peer review feedback regarding
infinite price handling in TASK-07.
"""

import numpy as np
import pandas as pd
import pytest

from src.room_type_analysis import analyze_prices_by_room_type


def test_positive_infinity_excluded_from_average():
    """Positive infinity must not affect the average price."""
    df = pd.DataFrame({
        "room_type": ["Private room", "Private room", "Private room"],
        "price": [100, 200, np.inf],
    })

    result = analyze_prices_by_room_type(df)

    assert result.iloc[0]["average_price"] == pytest.approx(150.0)
    assert np.isfinite(result.iloc[0]["average_price"])


def test_positive_infinity_excluded_from_listing_count():
    """Infinite prices must not be included in listing counts."""
    df = pd.DataFrame({
        "room_type": ["Private room", "Private room", "Private room"],
        "price": [100, 200, np.inf],
    })

    result = analyze_prices_by_room_type(df)

    assert result.iloc[0]["listing_count"] == 2


def test_negative_infinity_excluded():
    """Negative infinity must be excluded from price statistics."""
    df = pd.DataFrame({
        "room_type": ["Shared room", "Shared room"],
        "price": [50, -np.inf],
    })

    result = analyze_prices_by_room_type(df)

    assert result.iloc[0]["average_price"] == pytest.approx(50.0)
    assert result.iloc[0]["listing_count"] == 1


def test_median_excludes_infinite_prices():
    """Median must be calculated using only finite prices."""
    df = pd.DataFrame({
        "room_type": ["Entire home/apt"] * 4,
        "price": [100, 200, 300, np.inf],
    })

    result = analyze_prices_by_room_type(df)

    assert result.iloc[0]["median_price"] == pytest.approx(200.0)


def test_all_infinite_prices_raise_value_error():
    """An error must be raised when no valid prices remain."""
    df = pd.DataFrame({
        "room_type": ["Private room", "Shared room"],
        "price": [np.inf, -np.inf],
    })

    with pytest.raises(ValueError):
        analyze_prices_by_room_type(df)


def test_valid_prices_remain_unchanged():
    """Valid prices must still produce correct statistics."""
    df = pd.DataFrame({
        "room_type": ["Private room", "Private room"],
        "price": [100, 200],
    })

    result = analyze_prices_by_room_type(df)

    assert result.iloc[0]["average_price"] == pytest.approx(150.0)
    assert result.iloc[0]["median_price"] == pytest.approx(150.0)
    assert result.iloc[0]["listing_count"] == 2


def test_mixed_invalid_prices_excluded():
    """Zero, negative, NaN, and infinite prices must be excluded."""
    df = pd.DataFrame({
        "room_type": ["Private room"] * 6,
        "price": [100, 200, 0, -50, np.nan, np.inf],
    })

    result = analyze_prices_by_room_type(df)

    assert result.iloc[0]["average_price"] == pytest.approx(150.0)
    assert result.iloc[0]["listing_count"] == 2