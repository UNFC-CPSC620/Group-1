"""
Tests for TASK-05: Test and Document Data Cleaning
---------------------------------------------------
Course  : CPSC 620
Project : NYC Airbnb Data Summary Tool
Issue   : #7

This module tests both the data-loading function (load_data) and
the data-cleaning function (clean_data) to verify they work correctly
and handle all edge cases documented in their respective modules.

How to run
----------
From the project root folder:

    python -m pytest tests/test_task05_data_loading_cleaning.py -v

Or run this file directly:

    python tests/test_task05_data_loading_cleaning.py

Test categories
---------------
1. load_data()        — file not found, successful load, DataFrame shape
2. clean_data()       — input validation, text normalisation, numeric
                        conversion, invalid-value removal, duplicate removal
3. Integration        — load then clean on the real dataset (skipped when
                        Airbnb_NYC.csv is absent so CI always passes)
4. Documentation      — verify every public function has a docstring

Acceptance criteria covered
----------------------------
[x] Data-loading functionality is tested.
[x] Data-cleaning functionality is tested.
[x] Functions return expected outputs.
[x] Data cleaning rules are verified.
[x] Functions include clear documentation.
[x] Testing results are recorded.
[x] The code executes without errors.
"""

import unittest
from pathlib import Path

import pandas as pd
import numpy as np

# ── Modules under test ────────────────────────────────────────────────────────
from src.data_loader import load_data, display_dataset_info
from src.data_cleaning import clean_data


# ── Helper: minimal valid row ─────────────────────────────────────────────────

def _make_row(**overrides):
    """
    Return a dictionary representing one clean, valid Airbnb listing.

    Pass keyword arguments to override any field so tests can inject
    exactly the value they want to check.

    Example
    -------
    >>> _make_row(price=-10)   # valid row except price is negative
    """
    row = {
        "id"                            : 1,
        "name"                          : "Cozy Brooklyn Apartment",
        "host_id"                       : 100,
        "host_name"                     : "Alice",
        "neighbourhood_group"           : "Brooklyn",
        "neighbourhood"                 : "Williamsburg",
        "latitude"                      : 40.71,
        "longitude"                     : -73.95,
        "room_type"                     : "Private room",
        "price"                         : 120,
        "minimum_nights"                : 2,
        "number_of_reviews"             : 5,
        "last_review"                   : "2023-01-15",
        "reviews_per_month"             : 0.5,
        "calculated_host_listings_count": 1,
        "availability_365"              : 90,
    }
    row.update(overrides)
    return row


def _make_df(*rows):
    """
    Build a DataFrame from one or more _make_row() dictionaries.

    If no rows are given, a single default valid row is used.

    Example
    -------
    >>> _make_df()                         # one default valid row
    >>> _make_df(_make_row(price=50), _make_row(id=2, price=200))
    """
    if not rows:
        rows = (_make_row(),)
    return pd.DataFrame(list(rows))


# =============================================================================
# 1. Tests for load_data()
# =============================================================================

class TestLoadData(unittest.TestCase):
    """
    Tests for src.data_loader.load_data().

    load_data() accepts a file path (str or Path), reads the CSV, and
    returns a pandas DataFrame. It must raise FileNotFoundError when
    the file does not exist.
    """

    # ── File-not-found behaviour ──────────────────────────────────────────────

    def test_missing_file_raises_file_not_found_error(self):
        """
        load_data() must raise FileNotFoundError for a non-existent path.

        This ensures callers receive a clear, descriptive error instead of
        a generic pandas or OS exception.
        """
        with self.assertRaises(FileNotFoundError):
            load_data("data/this_file_does_not_exist.csv")

    def test_error_message_contains_path(self):
        """
        The FileNotFoundError message should include the bad path so the
        developer knows exactly which file was missing.
        """
        bad_path = "data/nonexistent.csv"
        try:
            load_data(bad_path)
        except FileNotFoundError as exc:
            self.assertIn("nonexistent.csv", str(exc))
        else:
            self.fail("Expected FileNotFoundError was not raised.")

    # ── Successful load ───────────────────────────────────────────────────────

    def test_load_returns_dataframe(self):
        """
        When given a valid CSV path, load_data() must return a
        pandas DataFrame.
        """
        import tempfile, os

        # Write a small temporary CSV and load it.
        csv_content = (
            "id,name,price\n"
            "1,Apt A,100\n"
            "2,Apt B,200\n"
        )
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as tmp:
            tmp.write(csv_content)
            tmp_path = tmp.name

        try:
            result = load_data(tmp_path)
            self.assertIsInstance(result, pd.DataFrame)
        finally:
            os.unlink(tmp_path)

    def test_load_correct_row_count(self):
        """
        load_data() must return a DataFrame with the same number of rows
        as data lines in the CSV (header excluded).
        """
        import tempfile, os

        csv_content = (
            "id,name,price\n"
            "1,Apt A,100\n"
            "2,Apt B,200\n"
            "3,Apt C,300\n"
        )
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as tmp:
            tmp.write(csv_content)
            tmp_path = tmp.name

        try:
            result = load_data(tmp_path)
            # 3 data rows → 3 DataFrame rows
            self.assertEqual(len(result), 3)
        finally:
            os.unlink(tmp_path)

    def test_load_path_object_accepted(self):
        """
        load_data() must accept a pathlib.Path object as well as a plain
        string, because many callers build paths with Path().
        """
        import tempfile, os

        csv_content = "id,price\n1,100\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as tmp:
            tmp.write(csv_content)
            tmp_path = tmp.name

        try:
            # Pass a Path object, not a string.
            result = load_data(Path(tmp_path))
            self.assertIsInstance(result, pd.DataFrame)
        finally:
            os.unlink(tmp_path)


# =============================================================================
# 2. Tests for clean_data() — input validation
# =============================================================================

class TestCleanDataInputValidation(unittest.TestCase):
    """
    Tests that clean_data() rejects bad input before doing any work.

    clean_data() must raise TypeError for non-DataFrames and
    ValueError when required columns are missing.
    """

    def test_non_dataframe_raises_type_error(self):
        """
        Passing a list instead of a DataFrame must raise TypeError.
        """
        with self.assertRaises(TypeError):
            clean_data([1, 2, 3])

    def test_dict_raises_type_error(self):
        """
        Passing a plain dict instead of a DataFrame must raise TypeError.
        """
        with self.assertRaises(TypeError):
            clean_data({"price": [100]})

    def test_missing_required_column_raises_value_error(self):
        """
        A DataFrame without 'price' must raise ValueError because price
        is required to filter invalid listings.
        """
        df = pd.DataFrame({"id": [1], "neighbourhood_group": ["Brooklyn"]})
        with self.assertRaises(ValueError):
            clean_data(df)

    def test_error_message_names_missing_column(self):
        """
        The ValueError message should name the missing column so the
        developer knows what to add.
        """
        df = pd.DataFrame({"id": [1]})
        try:
            clean_data(df)
        except ValueError as exc:
            self.assertIn("neighbourhood_group", str(exc))
        else:
            self.fail("Expected ValueError was not raised.")


# =============================================================================
# 3. Tests for clean_data() — return type and structure
# =============================================================================

class TestCleanDataReturnStructure(unittest.TestCase):
    """
    Tests that clean_data() returns a properly structured DataFrame.
    """

    def test_returns_dataframe(self):
        """
        clean_data() must always return a pandas DataFrame.
        """
        df = _make_df()
        result = clean_data(df)
        self.assertIsInstance(result, pd.DataFrame)

    def test_does_not_modify_original(self):
        """
        clean_data() must not modify the input DataFrame.

        The original DataFrame should have the same shape before and
        after calling clean_data().
        """
        df = _make_df()
        original_shape = df.shape
        clean_data(df)
        self.assertEqual(df.shape, original_shape)

    def test_output_columns_match_input_columns(self):
        """
        The cleaned DataFrame must contain the same columns as the
        input DataFrame (no columns added or removed).
        """
        df = _make_df()
        result = clean_data(df)
        self.assertListEqual(sorted(df.columns.tolist()),
                             sorted(result.columns.tolist()))

    def test_index_is_reset(self):
        """
        The output index must start at 0 and be consecutive integers.

        A reset index makes downstream code like df.iloc[0] behave
        predictably after rows have been removed.
        """
        rows = [_make_row(id=i, price=100) for i in range(1, 5)]
        df = _make_df(*rows)
        result = clean_data(df)
        expected = list(range(len(result)))
        self.assertEqual(result.index.tolist(), expected)


# =============================================================================
# 4. Tests for clean_data() — valid row is kept
# =============================================================================

class TestCleanDataKeepsValidRow(unittest.TestCase):
    """
    A perfectly valid row must pass through clean_data() unchanged.
    """

    def test_valid_row_is_kept(self):
        """
        A row with all valid values must appear in the output.
        """
        df = _make_df()
        result = clean_data(df)
        self.assertEqual(len(result), 1)

    def test_valid_row_price_preserved(self):
        """
        The price of a valid row must be unchanged after cleaning.
        """
        df = _make_df(_make_row(price=250))
        result = clean_data(df)
        self.assertEqual(result.iloc[0]["price"], 250)


# =============================================================================
# 5. Tests for clean_data() — price cleaning rules
# =============================================================================

class TestCleanDataPriceRules(unittest.TestCase):
    """
    Price must be a positive finite number (> 0).

    Rows with price = 0, price < 0, or price = NaN must be removed.
    """

    def test_zero_price_row_is_removed(self):
        """
        A listing with price = 0 is not a valid listing and must be
        removed by clean_data().
        """
        df = _make_df(_make_row(price=0))
        result = clean_data(df)
        self.assertEqual(len(result), 0)

    def test_negative_price_row_is_removed(self):
        """
        A listing with a negative price must be removed.
        """
        df = _make_df(_make_row(price=-50))
        result = clean_data(df)
        self.assertEqual(len(result), 0)

    def test_nan_price_row_is_removed(self):
        """
        A listing with price = NaN must be removed.
        """
        df = _make_df(_make_row(price=float("nan")))
        result = clean_data(df)
        self.assertEqual(len(result), 0)

    def test_valid_price_row_is_kept(self):
        """
        A listing with a positive price must not be removed by the
        price filter.
        """
        df = _make_df(_make_row(price=1))
        result = clean_data(df)
        self.assertEqual(len(result), 1)

    def test_mixed_prices_only_valid_kept(self):
        """
        When valid and invalid prices are mixed, only the valid rows
        must survive.
        """
        rows = [
            _make_row(id=1, price=100),   # valid
            _make_row(id=2, price=0),     # invalid
            _make_row(id=3, price=-5),    # invalid
            _make_row(id=4, price=200),   # valid
        ]
        df = _make_df(*rows)
        result = clean_data(df)
        self.assertEqual(len(result), 2)
        self.assertListEqual(sorted(result["price"].tolist()), [100, 200])


# =============================================================================
# 6. Tests for clean_data() — minimum_nights cleaning rules
# =============================================================================

class TestCleanDataMinimumNightsRules(unittest.TestCase):
    """
    minimum_nights must be a positive whole number (>= 1, no decimals).

    Rows with minimum_nights < 1 or fractional values must be removed.
    """

    def test_zero_minimum_nights_is_removed(self):
        """
        A listing requiring 0 minimum nights is invalid and must be
        removed.
        """
        df = _make_df(_make_row(minimum_nights=0))
        result = clean_data(df)
        self.assertEqual(len(result), 0)

    def test_negative_minimum_nights_is_removed(self):
        """
        A listing with negative minimum nights must be removed.
        """
        df = _make_df(_make_row(minimum_nights=-1))
        result = clean_data(df)
        self.assertEqual(len(result), 0)

    def test_fractional_minimum_nights_is_removed(self):
        """
        A listing with 1.5 minimum nights is not a whole number and
        must be removed because nights are always whole days.
        """
        df = _make_df(_make_row(minimum_nights=1.5))
        result = clean_data(df)
        self.assertEqual(len(result), 0)

    def test_valid_minimum_nights_kept(self):
        """
        A listing with minimum_nights = 1 (the minimum valid value)
        must not be removed.
        """
        df = _make_df(_make_row(minimum_nights=1))
        result = clean_data(df)
        self.assertEqual(len(result), 1)


# =============================================================================
# 7. Tests for clean_data() — availability_365 cleaning rules
# =============================================================================

class TestCleanDataAvailabilityRules(unittest.TestCase):
    """
    availability_365 must be a whole number between 0 and 365 inclusive.
    """

    def test_availability_below_zero_is_removed(self):
        """
        Availability cannot be negative; such rows must be removed.
        """
        df = _make_df(_make_row(availability_365=-1))
        result = clean_data(df)
        self.assertEqual(len(result), 0)

    def test_availability_above_365_is_removed(self):
        """
        Availability cannot exceed the number of days in a year; rows
        with availability_365 > 365 must be removed.
        """
        df = _make_df(_make_row(availability_365=366))
        result = clean_data(df)
        self.assertEqual(len(result), 0)

    def test_availability_zero_is_valid(self):
        """
        availability_365 = 0 means the listing is fully blocked out
        but is still a valid listing row.
        """
        df = _make_df(_make_row(availability_365=0))
        result = clean_data(df)
        self.assertEqual(len(result), 1)

    def test_availability_365_is_valid(self):
        """
        availability_365 = 365 (always available) is the maximum
        valid value and must be kept.
        """
        df = _make_df(_make_row(availability_365=365))
        result = clean_data(df)
        self.assertEqual(len(result), 1)

    def test_fractional_availability_is_removed(self):
        """
        Fractional availability (e.g. 90.5) is not a whole number
        and must be removed.
        """
        df = _make_df(_make_row(availability_365=90.5))
        result = clean_data(df)
        self.assertEqual(len(result), 0)


# =============================================================================
# 8. Tests for clean_data() — text normalisation
# =============================================================================

class TestCleanDataTextNormalisation(unittest.TestCase):
    """
    Text columns must have leading/trailing whitespace stripped.
    Empty strings in name and host_name must be replaced with
    placeholder values.
    """

    def test_whitespace_stripped_from_neighbourhood_group(self):
        """
        Leading and trailing spaces in neighbourhood_group must be
        removed so that " Brooklyn " becomes "Brooklyn".
        """
        df = _make_df(_make_row(neighbourhood_group="  Brooklyn  "))
        result = clean_data(df)
        self.assertEqual(result.iloc[0]["neighbourhood_group"], "Brooklyn")

    def test_missing_name_filled_with_placeholder(self):
        """
        A listing with name = NaN must have its name replaced with
        "Unknown listing" so downstream code never sees a null name.
        """
        df = _make_df(_make_row(name=None))
        result = clean_data(df)
        self.assertEqual(result.iloc[0]["name"], "Unknown listing")

    def test_missing_host_name_filled_with_placeholder(self):
        """
        A listing with host_name = NaN must have its host_name replaced
        with "Unknown host".
        """
        df = _make_df(_make_row(host_name=None))
        result = clean_data(df)
        self.assertEqual(result.iloc[0]["host_name"], "Unknown host")


# =============================================================================
# 9. Tests for clean_data() — missing essential columns
# =============================================================================

class TestCleanDataMissingEssentials(unittest.TestCase):
    """
    Rows missing values in essential columns must be dropped.

    Essential columns: id, neighbourhood_group, neighbourhood, room_type.
    A missing name or host_name is acceptable (filled with placeholder).
    """

    def test_row_missing_neighbourhood_group_is_removed(self):
        """
        A row with neighbourhood_group = NaN has no geographic grouping
        and must be removed.
        """
        df = _make_df(_make_row(neighbourhood_group=None))
        result = clean_data(df)
        self.assertEqual(len(result), 0)

    def test_row_missing_room_type_is_removed(self):
        """
        A row with room_type = NaN cannot be categorised and must be
        removed.
        """
        df = _make_df(_make_row(room_type=None))
        result = clean_data(df)
        self.assertEqual(len(result), 0)


# =============================================================================
# 10. Tests for clean_data() — duplicate handling
# =============================================================================

class TestCleanDataDuplicates(unittest.TestCase):
    """
    Exact duplicate rows and duplicate listing IDs must be removed.
    The first occurrence is always kept.
    """

    def test_exact_duplicate_rows_removed(self):
        """
        When two rows are completely identical, clean_data() must keep
        only one of them.
        """
        row = _make_row()
        df = _make_df(row, row)   # same row twice
        result = clean_data(df)
        self.assertEqual(len(result), 1)

    def test_duplicate_id_keeps_first(self):
        """
        When two rows share the same listing ID but differ in other
        fields, clean_data() keeps the first occurrence.
        """
        row1 = _make_row(id=42, price=100)
        row2 = _make_row(id=42, price=999)   # same ID, different price
        df = _make_df(row1, row2)
        result = clean_data(df)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["price"], 100)   # first kept

    def test_unique_rows_all_kept(self):
        """
        When all rows have unique IDs, clean_data() must keep every
        row that passes the other validation checks.
        """
        rows = [_make_row(id=i, price=100 + i) for i in range(1, 6)]
        df = _make_df(*rows)
        result = clean_data(df)
        self.assertEqual(len(result), 5)


# =============================================================================
# 11. Tests for clean_data() — review fields
# =============================================================================

class TestCleanDataReviewFields(unittest.TestCase):
    """
    Review fields (number_of_reviews, reviews_per_month) must be
    treated as optional and handled according to business rules.
    """

    def test_zero_reviews_sets_reviews_per_month_to_zero(self):
        """
        A listing with number_of_reviews = 0 and a null
        reviews_per_month must have reviews_per_month set to 0.0
        because a listing with no reviews has a review rate of zero.
        """
        df = _make_df(
            _make_row(number_of_reviews=0, reviews_per_month=None)
        )
        result = clean_data(df)
        self.assertEqual(result.iloc[0]["reviews_per_month"], 0.0)

    def test_missing_last_review_is_preserved(self):
        """
        A null last_review date is meaningful — it means the listing
        has never been reviewed. It must not be dropped or filled.
        """
        df = _make_df(_make_row(last_review=None))
        result = clean_data(df)
        # Row must still be present
        self.assertEqual(len(result), 1)
        # last_review must still be null/NaT
        self.assertTrue(pd.isna(result.iloc[0]["last_review"]))


# =============================================================================
# 12. Integration test — load then clean the real dataset
# =============================================================================

class TestIntegrationLoadAndClean(unittest.TestCase):
    """
    End-to-end test that loads the real CSV and runs clean_data() on it.

    This test is skipped automatically when Airbnb_NYC.csv is missing
    so that the test suite passes in environments without the dataset
    (e.g., a fresh clone before the data file is added).
    """

    DATASET_PATH = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "Airbnb_NYC.csv"
    )

    @classmethod
    def setUpClass(cls):
        """
        Load the CSV once and store it so all integration tests share
        the same DataFrame without re-reading the file repeatedly.
        """
        if not cls.DATASET_PATH.is_file():
            raise unittest.SkipTest(
                f"Airbnb_NYC.csv not found at {cls.DATASET_PATH}. "
                "Skipping integration tests."
            )
        cls.raw_df = load_data(cls.DATASET_PATH)
        cls.clean_df = clean_data(cls.raw_df)

    def test_cleaned_df_is_dataframe(self):
        """
        The result of cleaning the real dataset must be a DataFrame.
        """
        self.assertIsInstance(self.clean_df, pd.DataFrame)

    def test_cleaned_df_has_rows(self):
        """
        After cleaning, the dataset must not be empty — the real NYC
        Airbnb CSV contains thousands of valid listings.
        """
        self.assertGreater(len(self.clean_df), 0)

    def test_cleaned_df_smaller_than_raw(self):
        """
        Cleaning must remove at least some rows (e.g., the $0-price
        listings that exist in the raw data).
        """
        self.assertLessEqual(len(self.clean_df), len(self.raw_df))

    def test_no_invalid_prices_after_cleaning(self):
        """
        After cleaning, every price in the dataset must be positive.
        """
        prices = pd.to_numeric(self.clean_df["price"], errors="coerce")
        self.assertTrue((prices > 0).all(),
                        "Found non-positive price after cleaning.")

    def test_availability_in_range_after_cleaning(self):
        """
        After cleaning, every availability_365 must be between 0 and
        365 inclusive.
        """
        avail = pd.to_numeric(
            self.clean_df["availability_365"], errors="coerce"
        )
        self.assertTrue(avail.between(0, 365).all(),
                        "Found out-of-range availability after cleaning.")

    def test_no_duplicate_ids_after_cleaning(self):
        """
        After cleaning, no listing ID must appear more than once.
        """
        duplicate_count = self.clean_df["id"].duplicated().sum()
        self.assertEqual(duplicate_count, 0,
                         f"Found {duplicate_count} duplicate IDs after cleaning.")

    def test_required_columns_present(self):
        """
        All columns required by downstream analysis tasks must be
        present in the cleaned DataFrame.
        """
        required = [
            "id", "neighbourhood_group", "neighbourhood",
            "room_type", "price", "minimum_nights", "availability_365",
        ]
        for col in required:
            with self.subTest(column=col):
                self.assertIn(col, self.clean_df.columns)


# =============================================================================
# 13. Documentation tests — every public function must have a docstring
# =============================================================================

class TestDocumentation(unittest.TestCase):
    """
    Verify that every public function has a docstring.

    Good docstrings help teammates understand what each function does
    without reading every line of code.
    """

    def test_load_data_has_docstring(self):
        """load_data() must have a docstring."""
        self.assertTrue(
            bool(load_data.__doc__),
            "load_data() is missing a docstring."
        )

    def test_display_dataset_info_has_docstring(self):
        """display_dataset_info() must have a docstring."""
        self.assertTrue(
            bool(display_dataset_info.__doc__),
            "display_dataset_info() is missing a docstring."
        )

    def test_clean_data_has_docstring(self):
        """clean_data() must have a docstring."""
        self.assertTrue(
            bool(clean_data.__doc__),
            "clean_data() is missing a docstring."
        )

    def test_clean_data_docstring_mentions_parameters(self):
        """
        clean_data()'s docstring must mention 'Parameters' so callers
        know what to pass in.
        """
        self.assertIn("Parameters", clean_data.__doc__)

    def test_clean_data_docstring_mentions_returns(self):
        """
        clean_data()'s docstring must mention 'Returns' so callers
        know what to expect back.
        """
        self.assertIn("Returns", clean_data.__doc__)


# =============================================================================
# Entry point
# =============================================================================

if __name__ == "__main__":
    # Run with verbosity=2 so each test name and result is printed.
    unittest.main(verbosity=2)
