# =============================================================================
# test_task14_availability_analysis.py
# -----------------------------------------------------------------------------
# TASK-14: Test and Document Availability Analysis
#
# Unit and integration tests for two availability analysis modules:
#
#   src/availability_analysis.py
#       analyze_overall_availability(df) — overall stats across all listings
#
#   src/neighbourhood_availability.py
#       compare_availability_by_neighbourhood(df) — breakdown by borough
#
# Test categories
# ---------------
# 1. analyze_overall_availability()
#       - Input validation (missing column, wrong type)
#       - Return structure (keys, types)
#       - Correct computed values (mean, median, counts)
#       - Edge cases (all zeros, all 365, single row)
#
# 2. compare_availability_by_neighbourhood()
#       - Input validation (missing columns)
#       - Return structure (DataFrame, required columns)
#       - Correct grouping and aggregation
#       - Sorting (highest mean first)
#       - Text normalisation (strip + title-case)
#
# 3. Integration — load real CSV then run both functions
#
# 4. Documentation — public functions have docstrings
#
# Acceptance criteria covered
# ---------------------------
# [x] Availability analysis functionality is tested.
# [x] Functions return expected outputs.
# [x] Analysis rules are verified (stats, grouping, sorting).
# [x] Functions include clear documentation.
# [x] Testing results are recorded.
# [x] The code executes without errors.
#
# Authors  : Alejandro (Kvothep), Katerine (KaterineForero-dotcom)
# Issue    : #19
# Sprint   : Sprint 1
# =============================================================================

import unittest
from pathlib import Path

import pandas as pd
import numpy as np

from src.availability_analysis import analyze_overall_availability
from src.neighbourhood_availability import compare_availability_by_neighbourhood


# =============================================================================
# Helper — build a minimal valid Airbnb row
# =============================================================================

def _make_row(**overrides):
    """
    Return a dictionary representing one clean, valid Airbnb listing.

    Pass keyword arguments to override any field, so tests can inject
    exactly the value they want to check.

    Example
    -------
    >>> _make_row(availability_365=0, neighbourhood_group="Bronx")
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
# 1. Tests for analyze_overall_availability()
# =============================================================================

class TestAnalyzeOverallAvailabilityInputValidation(unittest.TestCase):
    """analyze_overall_availability() rejects bad inputs early."""

    def test_missing_availability_column_raises(self):
        """DataFrame without availability_365 must raise KeyError."""
        df = _make_df(_make_row())
        df = df.drop(columns=["availability_365"])
        with self.assertRaises(Exception):
            analyze_overall_availability(df)

    def test_non_dataframe_raises(self):
        """Passing a list instead of a DataFrame must raise an error."""
        with self.assertRaises(Exception):
            analyze_overall_availability([1, 2, 3])


class TestAnalyzeOverallAvailabilityReturnStructure(unittest.TestCase):
    """analyze_overall_availability() returns a dict with the required keys."""

    def setUp(self):
        df = _make_df(
            _make_row(availability_365=100),
            _make_row(id=2, availability_365=200),
            _make_row(id=3, availability_365=365),
        )
        self.result = analyze_overall_availability(df)

    def test_returns_dict(self):
        self.assertIsInstance(self.result, dict)

    def test_has_total_listings_key(self):
        self.assertIn("total_listings", self.result)

    def test_has_mean_availability_key(self):
        self.assertIn("mean_availability", self.result)

    def test_has_median_availability_key(self):
        self.assertIn("median_availability", self.result)

    def test_has_min_availability_key(self):
        self.assertIn("min_availability", self.result)

    def test_has_max_availability_key(self):
        self.assertIn("max_availability", self.result)

    def test_has_std_availability_key(self):
        self.assertIn("std_availability", self.result)

    def test_has_fully_available_key(self):
        self.assertIn("fully_available", self.result)

    def test_has_not_available_key(self):
        self.assertIn("not_available", self.result)


class TestAnalyzeOverallAvailabilityComputedValues(unittest.TestCase):
    """analyze_overall_availability() computes correct statistics."""

    def setUp(self):
        # Known values: 100, 200, 300 → mean=200, median=200, min=100, max=300
        self.df = _make_df(
            _make_row(id=1, availability_365=100),
            _make_row(id=2, availability_365=200),
            _make_row(id=3, availability_365=300),
        )
        self.result = analyze_overall_availability(self.df)

    def test_total_listings_correct(self):
        self.assertEqual(self.result["total_listings"], 3)

    def test_mean_availability_correct(self):
        self.assertAlmostEqual(self.result["mean_availability"], 200.0, places=1)

    def test_median_availability_correct(self):
        self.assertAlmostEqual(self.result["median_availability"], 200.0, places=1)

    def test_min_availability_correct(self):
        self.assertEqual(self.result["min_availability"], 100)

    def test_max_availability_correct(self):
        self.assertEqual(self.result["max_availability"], 300)

    def test_fully_available_count_correct(self):
        # None of our rows have availability_365 == 365
        self.assertEqual(self.result["fully_available"], 0)

    def test_not_available_count_correct(self):
        # None of our rows have availability_365 == 0
        self.assertEqual(self.result["not_available"], 0)


class TestAnalyzeOverallAvailabilityEdgeCases(unittest.TestCase):
    """analyze_overall_availability() handles boundary values correctly."""

    def test_all_zero_availability(self):
        """When all listings have 0 availability, not_available == total."""
        df = _make_df(
            _make_row(id=1, availability_365=0),
            _make_row(id=2, availability_365=0),
        )
        result = analyze_overall_availability(df)
        self.assertEqual(result["not_available"], 2)
        self.assertEqual(result["mean_availability"], 0.0)

    def test_all_fully_available(self):
        """When all listings have 365 days, fully_available == total."""
        df = _make_df(
            _make_row(id=1, availability_365=365),
            _make_row(id=2, availability_365=365),
        )
        result = analyze_overall_availability(df)
        self.assertEqual(result["fully_available"], 2)
        self.assertEqual(result["mean_availability"], 365.0)

    def test_single_row_dataset(self):
        """A single-row DataFrame should not crash and return correct values."""
        df = _make_df(_make_row(availability_365=180))
        result = analyze_overall_availability(df)
        self.assertEqual(result["total_listings"], 1)
        self.assertEqual(result["mean_availability"], 180.0)
        self.assertEqual(result["min_availability"], 180)
        self.assertEqual(result["max_availability"], 180)

    def test_mixed_zero_full_and_middle(self):
        """Dataset with 0, 365, and a middle value returns correct counts."""
        df = _make_df(
            _make_row(id=1, availability_365=0),
            _make_row(id=2, availability_365=182),
            _make_row(id=3, availability_365=365),
        )
        result = analyze_overall_availability(df)
        self.assertEqual(result["not_available"], 1)
        self.assertEqual(result["fully_available"], 1)


# =============================================================================
# 2. Tests for compare_availability_by_neighbourhood()
# =============================================================================

class TestCompareAvailabilityInputValidation(unittest.TestCase):
    """compare_availability_by_neighbourhood() rejects bad inputs."""

    def test_missing_neighbourhood_group_raises(self):
        """DataFrame without neighbourhood_group must raise an error."""
        df = _make_df(_make_row())
        df = df.drop(columns=["neighbourhood_group"])
        with self.assertRaises(Exception):
            compare_availability_by_neighbourhood(df)

    def test_missing_availability_column_raises(self):
        """DataFrame without availability_365 must raise an error."""
        df = _make_df(_make_row())
        df = df.drop(columns=["availability_365"])
        with self.assertRaises(Exception):
            compare_availability_by_neighbourhood(df)


class TestCompareAvailabilityReturnStructure(unittest.TestCase):
    """compare_availability_by_neighbourhood() returns the right shape."""

    def setUp(self):
        self.df = _make_df(
            _make_row(id=1, neighbourhood_group="Brooklyn",   availability_365=100),
            _make_row(id=2, neighbourhood_group="Manhattan",  availability_365=200),
            _make_row(id=3, neighbourhood_group="Queens",     availability_365=150),
        )
        self.result = compare_availability_by_neighbourhood(self.df)

    def test_returns_dataframe(self):
        self.assertIsInstance(self.result, pd.DataFrame)

    def test_has_neighbourhood_group_column(self):
        self.assertIn("neighbourhood_group", self.result.columns)

    def test_has_mean_availability_column(self):
        self.assertIn("mean_availability", self.result.columns)

    def test_has_median_availability_column(self):
        self.assertIn("median_availability", self.result.columns)

    def test_has_total_listings_column(self):
        self.assertIn("total_listings", self.result.columns)

    def test_one_row_per_neighbourhood(self):
        """Each neighbourhood group appears exactly once."""
        self.assertEqual(len(self.result), 3)


class TestCompareAvailabilityGrouping(unittest.TestCase):
    """compare_availability_by_neighbourhood() groups and aggregates correctly."""

    def setUp(self):
        # Brooklyn: 3 listings with availability 100, 200, 300 → mean=200
        # Manhattan: 1 listing with availability 50 → mean=50
        self.df = _make_df(
            _make_row(id=1, neighbourhood_group="Brooklyn",  availability_365=100),
            _make_row(id=2, neighbourhood_group="Brooklyn",  availability_365=200),
            _make_row(id=3, neighbourhood_group="Brooklyn",  availability_365=300),
            _make_row(id=4, neighbourhood_group="Manhattan", availability_365=50),
        )
        self.result = compare_availability_by_neighbourhood(self.df)

    def test_brooklyn_total_listings(self):
        brooklyn = self.result[self.result["neighbourhood_group"] == "Brooklyn"]
        self.assertEqual(brooklyn["total_listings"].values[0], 3)

    def test_brooklyn_mean_availability(self):
        brooklyn = self.result[self.result["neighbourhood_group"] == "Brooklyn"]
        self.assertAlmostEqual(brooklyn["mean_availability"].values[0], 200.0, places=1)

    def test_manhattan_total_listings(self):
        manhattan = self.result[self.result["neighbourhood_group"] == "Manhattan"]
        self.assertEqual(manhattan["total_listings"].values[0], 1)

    def test_manhattan_mean_availability(self):
        manhattan = self.result[self.result["neighbourhood_group"] == "Manhattan"]
        self.assertAlmostEqual(manhattan["mean_availability"].values[0], 50.0, places=1)


class TestCompareAvailabilitySorting(unittest.TestCase):
    """Results must be sorted highest mean availability first."""

    def test_sorted_descending_by_mean(self):
        df = _make_df(
            _make_row(id=1, neighbourhood_group="Bronx",     availability_365=50),
            _make_row(id=2, neighbourhood_group="Brooklyn",  availability_365=200),
            _make_row(id=3, neighbourhood_group="Manhattan", availability_365=100),
        )
        result = compare_availability_by_neighbourhood(df)
        means = result["mean_availability"].tolist()
        self.assertEqual(means, sorted(means, reverse=True))

    def test_highest_mean_is_first_row(self):
        df = _make_df(
            _make_row(id=1, neighbourhood_group="Queens",    availability_365=300),
            _make_row(id=2, neighbourhood_group="Manhattan", availability_365=100),
        )
        result = compare_availability_by_neighbourhood(df)
        self.assertEqual(result.iloc[0]["neighbourhood_group"], "Queens")


class TestCompareAvailabilityTextNormalisation(unittest.TestCase):
    """Neighbourhood group names are stripped and title-cased before grouping."""

    def test_whitespace_stripped(self):
        """'  Brooklyn  ' should be grouped with 'Brooklyn'."""
        df = _make_df(
            _make_row(id=1, neighbourhood_group="  Brooklyn  ", availability_365=100),
            _make_row(id=2, neighbourhood_group="Brooklyn",     availability_365=200),
        )
        result = compare_availability_by_neighbourhood(df)
        # Both rows belong to the same group — only one row in result
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["total_listings"], 2)

    def test_case_normalised(self):
        """'brooklyn' and 'BROOKLYN' should merge into one group."""
        df = _make_df(
            _make_row(id=1, neighbourhood_group="brooklyn",  availability_365=100),
            _make_row(id=2, neighbourhood_group="BROOKLYN",  availability_365=200),
        )
        result = compare_availability_by_neighbourhood(df)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["neighbourhood_group"], "Brooklyn")


# =============================================================================
# 3. Integration — load real CSV then run both functions
# =============================================================================

DATASET_PATH = Path(__file__).resolve().parent.parent / "data" / "Airbnb_NYC.csv"
SKIP_INTEGRATION = not DATASET_PATH.exists()
SKIP_REASON = "Airbnb_NYC.csv not present — skipping integration tests"


@unittest.skipIf(SKIP_INTEGRATION, SKIP_REASON)
class TestIntegrationAvailabilityAnalysis(unittest.TestCase):
    """End-to-end tests using the real NYC Airbnb dataset."""

    @classmethod
    def setUpClass(cls):
        from src.data_loader import load_data
        from src.data_cleaning import clean_data
        raw = load_data(DATASET_PATH)
        cls.df = clean_data(raw)
        cls.overall = analyze_overall_availability(cls.df.copy())
        cls.by_neighbourhood = compare_availability_by_neighbourhood(cls.df.copy())

    def test_overall_returns_dict(self):
        self.assertIsInstance(self.overall, dict)

    def test_overall_total_listings_positive(self):
        self.assertGreater(self.overall["total_listings"], 0)

    def test_overall_mean_in_valid_range(self):
        self.assertGreaterEqual(self.overall["mean_availability"], 0)
        self.assertLessEqual(self.overall["mean_availability"], 365)

    def test_overall_min_max_ordering(self):
        self.assertLessEqual(self.overall["min_availability"],
                             self.overall["max_availability"])

    def test_neighbourhood_returns_dataframe(self):
        self.assertIsInstance(self.by_neighbourhood, pd.DataFrame)

    def test_neighbourhood_has_five_boroughs(self):
        """NYC has exactly 5 neighbourhood groups in this dataset."""
        self.assertEqual(len(self.by_neighbourhood), 5)

    def test_neighbourhood_mean_in_valid_range(self):
        means = self.by_neighbourhood["mean_availability"]
        self.assertTrue((means >= 0).all())
        self.assertTrue((means <= 365).all())

    def test_neighbourhood_sorted_descending(self):
        means = self.by_neighbourhood["mean_availability"].tolist()
        self.assertEqual(means, sorted(means, reverse=True))

    def test_neighbourhood_total_listings_sums_to_overall(self):
        """Sum of per-neighbourhood counts must equal total in overall stats."""
        neighbourhood_total = self.by_neighbourhood["total_listings"].sum()
        self.assertEqual(neighbourhood_total, self.overall["total_listings"])


# =============================================================================
# 4. Documentation tests
# =============================================================================

class TestDocumentation(unittest.TestCase):
    """Every public function must have a complete docstring."""

    def test_analyze_overall_availability_has_docstring(self):
        self.assertIsNotNone(analyze_overall_availability.__doc__)
        self.assertGreater(len(analyze_overall_availability.__doc__ or ""), 10)

    def test_analyze_overall_availability_docstring_mentions_parameters(self):
        self.assertIn("Parameters", analyze_overall_availability.__doc__ or "")

    def test_analyze_overall_availability_docstring_mentions_returns(self):
        self.assertIn("Returns", analyze_overall_availability.__doc__ or "")

    def test_compare_availability_has_docstring(self):
        self.assertIsNotNone(compare_availability_by_neighbourhood.__doc__)
        self.assertGreater(len(compare_availability_by_neighbourhood.__doc__ or ""), 10)

    def test_compare_availability_docstring_mentions_parameters(self):
        self.assertIn("Parameters", compare_availability_by_neighbourhood.__doc__ or "")

    def test_compare_availability_docstring_mentions_returns(self):
        self.assertIn("Returns", compare_availability_by_neighbourhood.__doc__ or "")


# =============================================================================
# Entry point
# =============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
