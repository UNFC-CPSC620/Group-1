# =============================================================================
# test_task08_price_analysis.py
# -----------------------------------------------------------------------------
# TASK-08: Test and Document Price Analysis
#
# Unit and integration tests for two price analysis modules:
#
#   src/price_analysis.py
#       calculate_price_summary(df) — overall price stats across all listings
#
#   src/room_type_analysis.py
#       analyze_prices_by_room_type(df) — price breakdown by room type
#
# Test categories
# ---------------
# 1. calculate_price_summary()
#       - Input validation (missing column, wrong type, no valid prices)
#       - Return structure (keys, types)
#       - Correct computed values (mean, median, min, max, count)
#       - Edge cases (zero prices excluded, negative prices excluded,
#                     non-numeric values excluded, single valid row)
#
# 2. analyze_prices_by_room_type()
#       - Input validation (missing columns, no valid data)
#       - Return structure (DataFrame, required columns)
#       - Correct grouping and aggregation
#       - Sorting (alphabetical by room type)
#       - Text normalisation (strip + lower-case before grouping)
#       - Invalid price filtering (zero and negative excluded)
#
# 3. Integration — load real CSV then run both functions
#
# 4. Documentation — public functions have docstrings
#
# Acceptance criteria covered
# ---------------------------
# [x] Price analysis functionality is tested.
# [x] Functions return expected outputs.
# [x] Analysis rules are verified (stats, grouping, sorting).
# [x] Functions include clear documentation.
# [x] Testing results are recorded.
# [x] The code executes without errors.
#
# Authors  : Alejandro (Kvothep)
# Issue    : #11
# Sprint   : Sprint 1
# =============================================================================

import unittest
from pathlib import Path

import pandas as pd
import numpy as np

from src.price_analysis import calculate_price_summary
from src.room_type_analysis import analyze_prices_by_room_type


# =============================================================================
# Helper — build a minimal valid Airbnb row
# =============================================================================

def _make_row(**overrides):
    """
    Return a dictionary representing one clean, valid Airbnb listing.

    Pass keyword arguments to override any field so tests can inject
    exactly the value they need.

    Example
    -------
    >>> _make_row(price=150, room_type="Private room")
    """
    row = {
        "id": 1,
        "name": "Cozy Brooklyn Apartment",
        "host_id": 100,
        "host_name": "Alice",
        "neighbourhood_group": "Brooklyn",
        "neighbourhood": "Williamsburg",
        "latitude": 40.71,
        "longitude": -73.95,
        "room_type": "Private room",
        "price": 120,
        "minimum_nights": 2,
        "number_of_reviews": 10,
        "last_review": "2023-01-15",
        "reviews_per_month": 1.0,
        "calculated_host_listings_count": 1,
        "availability_365": 200,
    }
    row.update(overrides)
    return row


def _make_df(*rows):
    """Build a DataFrame from one or more row dicts produced by _make_row()."""
    return pd.DataFrame(list(rows))


# =============================================================================
# 1. Tests for calculate_price_summary()
# =============================================================================

class TestCalculatePriceSummaryInputValidation(unittest.TestCase):
    """calculate_price_summary() rejects bad inputs early."""

    def test_missing_price_column_raises(self):
        """DataFrame without price column must raise ValueError."""
        df = _make_df(_make_row())
        df = df.drop(columns=["price"])
        with self.assertRaises(ValueError):
            calculate_price_summary(df)

    def test_all_zero_prices_raises(self):
        """All-zero prices are invalid — must raise ValueError."""
        df = _make_df(
            _make_row(id=1, price=0),
            _make_row(id=2, price=0),
        )
        with self.assertRaises(ValueError):
            calculate_price_summary(df)

    def test_all_negative_prices_raises(self):
        """All-negative prices are invalid — must raise ValueError."""
        df = _make_df(
            _make_row(id=1, price=-10),
            _make_row(id=2, price=-50),
        )
        with self.assertRaises(ValueError):
            calculate_price_summary(df)

    def test_all_non_numeric_raises(self):
        """All non-numeric prices must raise ValueError."""
        df = _make_df(
            _make_row(id=1, price="N/A"),
            _make_row(id=2, price="unknown"),
        )
        with self.assertRaises(ValueError):
            calculate_price_summary(df)


class TestCalculatePriceSummaryReturnStructure(unittest.TestCase):
    """calculate_price_summary() returns a dict with the required keys."""

    def setUp(self):
        df = _make_df(
            _make_row(id=1, price=100),
            _make_row(id=2, price=200),
            _make_row(id=3, price=300),
        )
        self.result = calculate_price_summary(df)

    def test_returns_dict(self):
        self.assertIsInstance(self.result, dict)

    def test_has_average_price_key(self):
        self.assertIn("average_price", self.result)

    def test_has_median_price_key(self):
        self.assertIn("median_price", self.result)

    def test_has_minimum_price_key(self):
        self.assertIn("minimum_price", self.result)

    def test_has_maximum_price_key(self):
        self.assertIn("maximum_price", self.result)

    def test_has_valid_price_count_key(self):
        self.assertIn("valid_price_count", self.result)


class TestCalculatePriceSummaryComputedValues(unittest.TestCase):
    """calculate_price_summary() computes correct statistics."""

    def setUp(self):
        # Known values: 100, 200, 300 → mean=200, median=200, min=100, max=300
        self.df = _make_df(
            _make_row(id=1, price=100),
            _make_row(id=2, price=200),
            _make_row(id=3, price=300),
        )
        self.result = calculate_price_summary(self.df)

    def test_average_price_correct(self):
        self.assertAlmostEqual(self.result["average_price"], 200.0, places=1)

    def test_median_price_correct(self):
        self.assertAlmostEqual(self.result["median_price"], 200.0, places=1)

    def test_minimum_price_correct(self):
        self.assertEqual(self.result["minimum_price"], 100)

    def test_maximum_price_correct(self):
        self.assertEqual(self.result["maximum_price"], 300)

    def test_valid_price_count_correct(self):
        self.assertEqual(self.result["valid_price_count"], 3)


class TestCalculatePriceSummaryInvalidFiltering(unittest.TestCase):
    """calculate_price_summary() excludes invalid prices from stats."""

    def test_zero_price_excluded(self):
        """Zero price is invalid and must not affect the stats."""
        df = _make_df(
            _make_row(id=1, price=100),
            _make_row(id=2, price=0),   # invalid
        )
        result = calculate_price_summary(df)
        self.assertAlmostEqual(result["average_price"], 100.0, places=1)
        self.assertEqual(result["valid_price_count"], 1)

    def test_negative_price_excluded(self):
        """Negative price is invalid and must not affect the stats."""
        df = _make_df(
            _make_row(id=1, price=150),
            _make_row(id=2, price=-50),  # invalid
        )
        result = calculate_price_summary(df)
        self.assertAlmostEqual(result["average_price"], 150.0, places=1)
        self.assertEqual(result["valid_price_count"], 1)

    def test_non_numeric_price_excluded(self):
        """Non-numeric price must be coerced to NaN and excluded."""
        df = _make_df(
            _make_row(id=1, price=200),
            _make_row(id=2, price="free"),  # invalid
        )
        result = calculate_price_summary(df)
        self.assertAlmostEqual(result["average_price"], 200.0, places=1)
        self.assertEqual(result["valid_price_count"], 1)

    def test_valid_count_excludes_invalid_rows(self):
        """valid_price_count counts only rows with price > 0."""
        df = _make_df(
            _make_row(id=1, price=100),
            _make_row(id=2, price=200),
            _make_row(id=3, price=0),    # invalid
            _make_row(id=4, price=-10),  # invalid
        )
        result = calculate_price_summary(df)
        self.assertEqual(result["valid_price_count"], 2)

    def test_single_valid_row(self):
        """A single valid price row should not crash."""
        df = _make_df(_make_row(id=1, price=99))
        result = calculate_price_summary(df)
        self.assertEqual(result["valid_price_count"], 1)
        self.assertAlmostEqual(result["average_price"], 99.0, places=1)
        self.assertEqual(result["minimum_price"], 99)
        self.assertEqual(result["maximum_price"], 99)


# =============================================================================
# 2. Tests for analyze_prices_by_room_type()
# =============================================================================

class TestAnalyzePricesByRoomTypeInputValidation(unittest.TestCase):
    """analyze_prices_by_room_type() rejects bad inputs."""

    def test_missing_room_type_column_raises(self):
        """DataFrame without room_type must raise ValueError."""
        df = _make_df(_make_row())
        df = df.drop(columns=["room_type"])
        with self.assertRaises(ValueError):
            analyze_prices_by_room_type(df)

    def test_missing_price_column_raises(self):
        """DataFrame without price must raise ValueError."""
        df = _make_df(_make_row())
        df = df.drop(columns=["price"])
        with self.assertRaises(ValueError):
            analyze_prices_by_room_type(df)

    def test_no_valid_data_raises(self):
        """All-invalid prices with valid room types must raise ValueError."""
        df = _make_df(
            _make_row(id=1, room_type="Private room", price=0),
            _make_row(id=2, room_type="Entire home/apt", price=-5),
        )
        with self.assertRaises(ValueError):
            analyze_prices_by_room_type(df)


class TestAnalyzePricesByRoomTypeReturnStructure(unittest.TestCase):
    """analyze_prices_by_room_type() returns the right shape."""

    def setUp(self):
        self.df = _make_df(
            _make_row(id=1, room_type="Private room",   price=100),
            _make_row(id=2, room_type="Entire home/apt", price=200),
            _make_row(id=3, room_type="Shared room",    price=50),
        )
        self.result = analyze_prices_by_room_type(self.df)

    def test_returns_dataframe(self):
        self.assertIsInstance(self.result, pd.DataFrame)

    def test_has_room_type_column(self):
        self.assertIn("room_type", self.result.columns)

    def test_has_average_price_column(self):
        self.assertIn("average_price", self.result.columns)

    def test_has_median_price_column(self):
        self.assertIn("median_price", self.result.columns)

    def test_has_listing_count_column(self):
        self.assertIn("listing_count", self.result.columns)

    def test_one_row_per_room_type(self):
        """Each room type appears exactly once."""
        self.assertEqual(len(self.result), 3)


class TestAnalyzePricesByRoomTypeGrouping(unittest.TestCase):
    """analyze_prices_by_room_type() groups and aggregates correctly."""

    def setUp(self):
        # Private room: 3 listings at 100, 200, 300 → mean=200
        # Entire home/apt: 1 listing at 500 → mean=500
        self.df = _make_df(
            _make_row(id=1, room_type="Private room",    price=100),
            _make_row(id=2, room_type="Private room",    price=200),
            _make_row(id=3, room_type="Private room",    price=300),
            _make_row(id=4, room_type="Entire home/apt", price=500),
        )
        self.result = analyze_prices_by_room_type(self.df)

    def test_private_room_listing_count(self):
        row = self.result[self.result["room_type"] == "private room"]
        self.assertEqual(row["listing_count"].values[0], 3)

    def test_private_room_average_price(self):
        row = self.result[self.result["room_type"] == "private room"]
        self.assertAlmostEqual(row["average_price"].values[0], 200.0, places=1)

    def test_entire_home_listing_count(self):
        row = self.result[self.result["room_type"] == "entire home/apt"]
        self.assertEqual(row["listing_count"].values[0], 1)

    def test_entire_home_average_price(self):
        row = self.result[self.result["room_type"] == "entire home/apt"]
        self.assertAlmostEqual(row["average_price"].values[0], 500.0, places=1)


class TestAnalyzePricesByRoomTypeSorting(unittest.TestCase):
    """Results must be sorted alphabetically by room type."""

    def test_sorted_alphabetically(self):
        df = _make_df(
            _make_row(id=1, room_type="Shared room",     price=50),
            _make_row(id=2, room_type="Private room",    price=100),
            _make_row(id=3, room_type="Entire home/apt", price=200),
        )
        result = analyze_prices_by_room_type(df)
        room_types = result["room_type"].tolist()
        self.assertEqual(room_types, sorted(room_types))


class TestAnalyzePricesByRoomTypeTextNormalisation(unittest.TestCase):
    """Room type names are stripped and lower-cased before grouping."""

    def test_whitespace_stripped(self):
        """'  Private room  ' should merge with 'Private room'."""
        df = _make_df(
            _make_row(id=1, room_type="  Private room  ", price=100),
            _make_row(id=2, room_type="Private room",     price=200),
        )
        result = analyze_prices_by_room_type(df)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["listing_count"], 2)

    def test_case_normalised(self):
        """'PRIVATE ROOM' and 'Private room' should merge into one group."""
        df = _make_df(
            _make_row(id=1, room_type="PRIVATE ROOM", price=100),
            _make_row(id=2, room_type="Private room", price=200),
        )
        result = analyze_prices_by_room_type(df)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["room_type"], "private room")


class TestAnalyzePricesByRoomTypeInvalidPrices(unittest.TestCase):
    """Zero and negative prices must be excluded from room type stats."""

    def test_zero_price_excluded_from_average(self):
        """A listing with price 0 must not affect the group average."""
        df = _make_df(
            _make_row(id=1, room_type="Private room", price=100),
            _make_row(id=2, room_type="Private room", price=0),   # invalid
        )
        result = analyze_prices_by_room_type(df)
        row = result[result["room_type"] == "private room"]
        self.assertAlmostEqual(row["average_price"].values[0], 100.0, places=1)

    def test_negative_price_excluded(self):
        """A listing with a negative price must be excluded."""
        df = _make_df(
            _make_row(id=1, room_type="Shared room", price=50),
            _make_row(id=2, room_type="Shared room", price=-10),  # invalid
        )
        result = analyze_prices_by_room_type(df)
        row = result[result["room_type"] == "shared room"]
        self.assertEqual(row["listing_count"].values[0], 1)


# =============================================================================
# 3. Integration — load real CSV then run both functions
# =============================================================================

DATASET_PATH = Path(__file__).resolve().parent.parent / "data" / "Airbnb_NYC.csv"
SKIP_INTEGRATION = not DATASET_PATH.exists()
SKIP_REASON = "Airbnb_NYC.csv not present — skipping integration tests"


@unittest.skipIf(SKIP_INTEGRATION, SKIP_REASON)
class TestIntegrationPriceAnalysis(unittest.TestCase):
    """End-to-end tests using the real NYC Airbnb dataset."""

    @classmethod
    def setUpClass(cls):
        from src.data_loader import load_data
        from src.data_cleaning import clean_data
        raw = load_data(DATASET_PATH)
        cls.df = clean_data(raw)
        cls.summary = calculate_price_summary(cls.df.copy())
        cls.by_room = analyze_prices_by_room_type(cls.df.copy())

    def test_summary_returns_dict(self):
        self.assertIsInstance(self.summary, dict)

    def test_summary_valid_price_count_positive(self):
        self.assertGreater(self.summary["valid_price_count"], 0)

    def test_summary_average_price_positive(self):
        self.assertGreater(self.summary["average_price"], 0)

    def test_summary_min_less_than_max(self):
        self.assertLessEqual(self.summary["minimum_price"],
                             self.summary["maximum_price"])

    def test_by_room_returns_dataframe(self):
        self.assertIsInstance(self.by_room, pd.DataFrame)

    def test_by_room_has_expected_columns(self):
        for col in ["room_type", "average_price", "median_price", "listing_count"]:
            self.assertIn(col, self.by_room.columns)

    def test_by_room_all_average_prices_positive(self):
        self.assertTrue((self.by_room["average_price"] > 0).all())

    def test_by_room_sorted_alphabetically(self):
        room_types = self.by_room["room_type"].tolist()
        self.assertEqual(room_types, sorted(room_types))

    def test_by_room_listing_count_sums_to_valid_total(self):
        """Sum of per-room-type counts must be <= overall valid_price_count."""
        self.assertLessEqual(
            self.by_room["listing_count"].sum(),
            self.summary["valid_price_count"]
        )


# =============================================================================
# 4. Documentation tests
# =============================================================================

class TestDocumentation(unittest.TestCase):
    """Every public function must have a complete docstring."""

    def test_calculate_price_summary_has_docstring(self):
        self.assertIsNotNone(calculate_price_summary.__doc__)
        self.assertGreater(len(calculate_price_summary.__doc__ or ""), 10)

    def test_calculate_price_summary_docstring_mentions_parameters(self):
        self.assertIn("Parameters", calculate_price_summary.__doc__ or "")

    def test_calculate_price_summary_docstring_mentions_returns(self):
        self.assertIn("Returns", calculate_price_summary.__doc__ or "")

    def test_analyze_prices_by_room_type_has_docstring(self):
        self.assertIsNotNone(analyze_prices_by_room_type.__doc__)
        self.assertGreater(len(analyze_prices_by_room_type.__doc__ or ""), 10)

    def test_analyze_prices_by_room_type_docstring_mentions_parameters(self):
        self.assertIn("Parameters", analyze_prices_by_room_type.__doc__ or "")

    def test_analyze_prices_by_room_type_docstring_mentions_returns(self):
        self.assertIn("Returns", analyze_prices_by_room_type.__doc__ or "")


# =============================================================================
# Entry point
# =============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
