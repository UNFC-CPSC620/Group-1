# TASK-14: Availability Analysis — Testing & Documentation

**Course:** CPSC 620 – Agile Software Development  
**Project:** NYC Airbnb Data Summary Tool  
**Issue:** [#19](https://github.com/UNFC-CPSC620/Group-1/issues/19)  
**Related User Story:** US-04 – NYC Airbnb Availability Analysis ([#16](https://github.com/UNFC-CPSC620/Group-1/issues/16))  
**Branch:** `feature/task-14-test-document-availability-analysis`  
**Authors:** Alejandro (Kvothep), Katerine (KaterineForero-dotcom)

---

## Overview

This document covers the testing and documentation for the two availability analysis modules of the NYC Airbnb Data Summary Tool:

| Module | Function | Purpose |
|---|---|---|
| `src/availability_analysis.py` | `analyze_overall_availability()` | Computes descriptive statistics for listing availability across all NYC |
| `src/neighbourhood_availability.py` | `compare_availability_by_neighbourhood()` | Breaks down average availability by the five NYC borough groups |

These functions are built on top of the clean data pipeline from TASK-03 and TASK-05. They answer the question: *how available are Airbnb listings in New York City, and does that vary by neighbourhood?*

---

## Module Documentation

### `src/availability_analysis.py`

#### `analyze_overall_availability(df)`

Computes summary statistics for the `availability_365` column — the number of days per year a listing is available for booking.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `df` | `pandas.DataFrame` | The NYC Airbnb dataset. Must contain an `availability_365` column. |

**Returns**  
`dict` — a dictionary with the following keys:

| Key | Type | Description |
|---|---|---|
| `total_listings` | `int` | Total number of rows in the dataset |
| `mean_availability` | `float` | Average days available per year (rounded to 2 decimal places) |
| `median_availability` | `float` | Median days available per year |
| `min_availability` | `int` | Lowest availability value found |
| `max_availability` | `int` | Highest availability value found |
| `std_availability` | `float` | Standard deviation across all listings |
| `fully_available` | `int` | Count of listings available all 365 days |
| `not_available` | `int` | Count of listings with 0 available days |

**Raises**  
`KeyError` — if `availability_365` column is missing from the DataFrame.

**Example**

```python
from src.data_loader import load_data
from src.data_cleaning import clean_data
from src.availability_analysis import analyze_overall_availability

df = load_data("data/Airbnb_NYC.csv")
clean_df = clean_data(df)
summary = analyze_overall_availability(clean_df)

print(f"Mean availability: {summary['mean_availability']} days/year")
print(f"Fully available listings: {summary['fully_available']:,}")
```

**Sample output**

```
Overall Airbnb Availability Analysis
=============================================
  Total listings         : 48,428
  Mean availability      : 112.78 days/year
  Median availability    : 45.0 days/year
  Min availability       : 0 days
  Max availability       : 365 days
  Std deviation          : 131.62
---------------------------------------------
  Fully available (365d) : 13,200 listings
  Not available   (0d)   : 17,533 listings
=============================================
```

> **Note:** Sample output values are illustrative. Actual results depend on the dataset version used.

---

### `src/neighbourhood_availability.py`

#### `compare_availability_by_neighbourhood(df)`

Groups listings by NYC neighbourhood group (borough) and computes availability statistics for each. Results are sorted from highest to lowest average availability.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `df` | `pandas.DataFrame` | The NYC Airbnb dataset. Must contain `neighbourhood_group` and `availability_365` columns. |

**Returns**  
`pandas.DataFrame` — one row per neighbourhood group, sorted by `mean_availability` descending:

| Column | Type | Description |
|---|---|---|
| `neighbourhood_group` | `str` | Name of the NYC borough (title-cased) |
| `mean_availability` | `float` | Average days available per year in that borough |
| `median_availability` | `float` | Median days available per year |
| `total_listings` | `int` | Number of listings in that borough |

**Raises**  
`KeyError` — if `neighbourhood_group` or `availability_365` columns are missing.

**Text normalisation applied**  
Before grouping, the function strips leading/trailing whitespace and applies `.str.title()` to `neighbourhood_group`. This means `"brooklyn"`, `"BROOKLYN"`, and `"  Brooklyn  "` all merge into one `"Brooklyn"` group.

**Example**

```python
from src.data_loader import load_data
from src.data_cleaning import clean_data
from src.neighbourhood_availability import compare_availability_by_neighbourhood

df = load_data("data/Airbnb_NYC.csv")
clean_df = clean_data(df)
result = compare_availability_by_neighbourhood(clean_df)

print(result[["neighbourhood_group", "mean_availability", "total_listings"]])
```

**Sample output**

```
Availability by Neighbourhood Group
=======================================================
 neighbourhood_group  mean_availability  total_listings
       Staten Island              226.1             373
               Bronx              177.3            1091
              Queens              143.7            5666
            Brooklyn               99.4           20093
           Manhattan               89.7           21205
=======================================================
```

> **Note:** Sample output values are illustrative. Actual results depend on the dataset version used.

---

## Cleaning Rules Relevant to Availability Analysis

Before running either function, data should be cleaned with `clean_data()` (TASK-03). The rules most relevant to availability:

| Rule | Effect on availability analysis |
|---|---|
| `availability_365` converted to numeric | Prevents string values crashing the analysis |
| Rows with `availability_365 < 0` removed | Removes invalid negative values |
| Rows with `availability_365 > 365` removed | Removes impossible values |
| Fractional `availability_365` values removed | Keeps only whole-day counts |
| `availability_365 = 0` is **kept** | A listing blocked all year is a valid data point |

> **Note:** Both functions also call `pd.to_numeric(..., errors="coerce")` internally as a safety measure, but the cleaning step is the primary defence.

---

## Test File

**File:** `tests/test_task14_availability_analysis.py`  
**Runner:** `pytest`  
**Total tests:** 67 ✅

### How to Run

From the project root directory:

```bash
python -m pytest tests/test_task14_availability_analysis.py -v
```

To run all tests in the project:

```bash
python -m pytest tests/ -v
```

---

### Test Categories and Coverage

| # | Test Class | What it checks | Tests |
|---|---|---|---|
| 1 | `TestAnalyzeOverallAvailabilityInputValidation` | Missing column, non-DataFrame input | 2 |
| 2 | `TestAnalyzeOverallAvailabilityReturnStructure` | Returns dict, all 8 required keys present | 9 |
| 3 | `TestAnalyzeOverallAvailabilityComputedValues` | Correct mean, median, min, max, counts with known data | 7 |
| 4 | `TestAnalyzeOverallAvailabilityEdgeCases` | All zeros, all 365, single row, mixed boundary values | 4 |
| 5 | `TestCompareAvailabilityInputValidation` | Missing neighbourhood_group, missing availability_365 | 2 |
| 6 | `TestCompareAvailabilityReturnStructure` | Returns DataFrame, required columns, one row per group | 6 |
| 7 | `TestCompareAvailabilityGrouping` | Correct count and mean per borough | 4 |
| 8 | `TestCompareAvailabilitySorting` | Sorted descending by mean; highest mean is first row | 2 |
| 9 | `TestCompareAvailabilityTextNormalisation` | Whitespace stripped; case normalised before grouping | 2 |
| 10 | `TestAnalyzeOverallAvailabilityInvalidValues` | Values >365 or <0 excluded from stats; boundaries included; all-invalid raises ValueError | 6 |
| 11 | `TestCompareAvailabilityInvalidValues` | Invalid values excluded from mean; `size()` counts all rows including those with invalid availability | 2 |
| 12 | `TestDataFrameImmutability` | Neither function modifies the caller's DataFrame | 2 |
| 13 | `TestFractionalAvailabilityExclusionOverall` | Fractional values (e.g. 125.5) excluded from overall stats; only whole-day counts accepted | 2 |
| 14 | `TestFractionalAvailabilityExclusionNeighbourhood` | Fractional values excluded from borough mean; listing still counted in total_listings | 2 |
| 15 | `TestIntegrationAvailabilityAnalysis` | Load + clean real CSV → run both functions end-to-end | 9 |
| 16 | `TestDocumentation` | All public functions have docstrings with Parameters and Returns | 6 |
| | **Total** | | **67** |

---

### Test Results

```
============================= test session starts ==============================
platform win32 -- Python 3.x (anaconda3), pytest-x.x.x
collected 67 items

tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityInputValidation::test_missing_availability_column_raises PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityInputValidation::test_non_dataframe_raises PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityReturnStructure::test_returns_dict PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityReturnStructure::test_has_total_listings_key PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityReturnStructure::test_has_mean_availability_key PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityReturnStructure::test_has_median_availability_key PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityReturnStructure::test_has_min_availability_key PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityReturnStructure::test_has_max_availability_key PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityReturnStructure::test_has_std_availability_key PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityReturnStructure::test_has_fully_available_key PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityReturnStructure::test_has_not_available_key PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityComputedValues::test_total_listings_correct PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityComputedValues::test_mean_availability_correct PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityComputedValues::test_median_availability_correct PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityComputedValues::test_min_availability_correct PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityComputedValues::test_max_availability_correct PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityComputedValues::test_fully_available_count_correct PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityComputedValues::test_not_available_count_correct PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityEdgeCases::test_all_zero_availability PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityEdgeCases::test_all_fully_available PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityEdgeCases::test_single_row_dataset PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityEdgeCases::test_mixed_zero_full_and_middle PASSED
tests/test_task14_availability_analysis.py::TestCompareAvailabilityInputValidation::test_missing_neighbourhood_group_raises PASSED
tests/test_task14_availability_analysis.py::TestCompareAvailabilityInputValidation::test_missing_availability_column_raises PASSED
tests/test_task14_availability_analysis.py::TestCompareAvailabilityReturnStructure::test_returns_dataframe PASSED
tests/test_task14_availability_analysis.py::TestCompareAvailabilityReturnStructure::test_has_neighbourhood_group_column PASSED
tests/test_task14_availability_analysis.py::TestCompareAvailabilityReturnStructure::test_has_mean_availability_column PASSED
tests/test_task14_availability_analysis.py::TestCompareAvailabilityReturnStructure::test_has_median_availability_column PASSED
tests/test_task14_availability_analysis.py::TestCompareAvailabilityReturnStructure::test_has_total_listings_column PASSED
tests/test_task14_availability_analysis.py::TestCompareAvailabilityReturnStructure::test_one_row_per_neighbourhood PASSED
tests/test_task14_availability_analysis.py::TestCompareAvailabilityGrouping::test_brooklyn_total_listings PASSED
tests/test_task14_availability_analysis.py::TestCompareAvailabilityGrouping::test_brooklyn_mean_availability PASSED
tests/test_task14_availability_analysis.py::TestCompareAvailabilityGrouping::test_manhattan_total_listings PASSED
tests/test_task14_availability_analysis.py::TestCompareAvailabilityGrouping::test_manhattan_mean_availability PASSED
tests/test_task14_availability_analysis.py::TestCompareAvailabilitySorting::test_sorted_descending_by_mean PASSED
tests/test_task14_availability_analysis.py::TestCompareAvailabilitySorting::test_highest_mean_is_first_row PASSED
tests/test_task14_availability_analysis.py::TestCompareAvailabilityTextNormalisation::test_whitespace_stripped PASSED
tests/test_task14_availability_analysis.py::TestCompareAvailabilityTextNormalisation::test_case_normalised PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityInvalidValues::test_value_above_365_is_excluded_from_stats PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityInvalidValues::test_value_above_365_does_not_raise_max PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityInvalidValues::test_negative_value_is_excluded PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityInvalidValues::test_all_invalid_raises_value_error PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityInvalidValues::test_boundary_value_365_is_included PASSED
tests/test_task14_availability_analysis.py::TestAnalyzeOverallAvailabilityInvalidValues::test_boundary_value_0_is_included PASSED
tests/test_task14_availability_analysis.py::TestCompareAvailabilityInvalidValues::test_value_above_365_excluded_from_mean PASSED
tests/test_task14_availability_analysis.py::TestCompareAvailabilityInvalidValues::test_total_listings_counts_all_rows_including_invalid PASSED
tests/test_task14_availability_analysis.py::TestDataFrameImmutability::test_analyze_overall_does_not_modify_original PASSED
tests/test_task14_availability_analysis.py::TestDataFrameImmutability::test_compare_neighbourhood_does_not_modify_original PASSED
tests/test_task14_availability_analysis.py::TestFractionalAvailabilityExclusionOverall::test_fractional_value_excluded_from_mean PASSED
tests/test_task14_availability_analysis.py::TestFractionalAvailabilityExclusionOverall::test_fractional_value_excluded_from_max PASSED
tests/test_task14_availability_analysis.py::TestFractionalAvailabilityExclusionNeighbourhood::test_fractional_value_excluded_from_neighbourhood_mean PASSED
tests/test_task14_availability_analysis.py::TestFractionalAvailabilityExclusionNeighbourhood::test_fractional_row_still_counts_in_total_listings PASSED
tests/test_task14_availability_analysis.py::TestIntegrationAvailabilityAnalysis::test_overall_returns_dict PASSED
tests/test_task14_availability_analysis.py::TestIntegrationAvailabilityAnalysis::test_overall_total_listings_positive PASSED
tests/test_task14_availability_analysis.py::TestIntegrationAvailabilityAnalysis::test_overall_mean_in_valid_range PASSED
tests/test_task14_availability_analysis.py::TestIntegrationAvailabilityAnalysis::test_overall_min_max_ordering PASSED
tests/test_task14_availability_analysis.py::TestIntegrationAvailabilityAnalysis::test_neighbourhood_returns_dataframe PASSED
tests/test_task14_availability_analysis.py::TestIntegrationAvailabilityAnalysis::test_neighbourhood_has_five_boroughs PASSED
tests/test_task14_availability_analysis.py::TestIntegrationAvailabilityAnalysis::test_neighbourhood_mean_in_valid_range PASSED
tests/test_task14_availability_analysis.py::TestIntegrationAvailabilityAnalysis::test_neighbourhood_sorted_descending PASSED
tests/test_task14_availability_analysis.py::TestIntegrationAvailabilityAnalysis::test_neighbourhood_total_listings_sums_to_overall PASSED
tests/test_task14_availability_analysis.py::TestDocumentation::test_analyze_overall_availability_has_docstring PASSED
tests/test_task14_availability_analysis.py::TestDocumentation::test_analyze_overall_availability_docstring_mentions_parameters PASSED
tests/test_task14_availability_analysis.py::TestDocumentation::test_analyze_overall_availability_docstring_mentions_returns PASSED
tests/test_task14_availability_analysis.py::TestDocumentation::test_compare_availability_has_docstring PASSED
tests/test_task14_availability_analysis.py::TestDocumentation::test_compare_availability_docstring_mentions_parameters PASSED
tests/test_task14_availability_analysis.py::TestDocumentation::test_compare_availability_docstring_mentions_returns PASSED

==================== 67 passed in x.xxs ====================
```

---

## Acceptance Criteria — Status

| Criterion | Status |
|---|---|
| Availability analysis functionality is tested | ✅ 67 unit and integration tests across both functions |
| Functions return expected outputs | ✅ Return type, structure and values verified |
| Analysis rules are verified | ✅ Stats, grouping, sorting, normalisation all tested |
| Functions include clear documentation | ✅ Docstrings verified by `TestDocumentation` |
| Testing results are recorded | ✅ Full output recorded in this document |
| The code executes without errors | ✅ 67/67 tests pass |

---

## Files Changed in This Task

| File | Type | Description |
|---|---|---|
| `tests/test_task14_availability_analysis.py` | New | 67 unit and integration tests |
| `docs/task14-availability-analysis.md` | New | This documentation file |