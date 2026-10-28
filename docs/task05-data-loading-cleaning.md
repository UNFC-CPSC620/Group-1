# TASK-05: Data Loading and Cleaning — Testing & Documentation

**Course:** CPSC 620 – Agile Software Development  
**Project:** NYC Airbnb Data Summary Tool  
**Issue:** [#7](https://github.com/UNFC-CPSC620/group-1/issues/7)  
**Related User Story:** US-01 – Data Loading and Cleaning ([#1](https://github.com/UNFC-CPSC620/group-1/issues/1))  
**Branch:** `feature/task-05-test-document-data-cleaning`

---

## Overview

This document covers the testing and documentation for two core modules of the NYC Airbnb Data Summary Tool:

| Module | Function | Purpose |
|---|---|---|
| `src/data_loader.py` | `load_data()` | Reads the CSV dataset into a pandas DataFrame |
| `src/data_loader.py` | `display_dataset_info()` | Prints dataset dimensions and column names |
| `src/data_cleaning.py` | `clean_data()` | Removes invalid, inconsistent, and duplicate rows |

These functions are the foundation of the pipeline — every downstream analysis task (price, availability, neighbourhood) depends on receiving clean, well-structured data.

---

## Module Documentation

### `src/data_loader.py`

#### `load_data(file_path)`

Loads the NYC Airbnb CSV dataset from disk and returns it as a pandas DataFrame.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `file_path` | `str` or `pathlib.Path` | Path to the CSV file on disk |

**Returns**  
`pandas.DataFrame` — the raw dataset with all original columns intact.

**Raises**  
`FileNotFoundError` — if the file does not exist at the given path. The error message includes the path so the developer knows exactly what was not found.

**Example**

```python
from pathlib import Path
from src.data_loader import load_data

dataset_path = Path("data/Airbnb_NYC.csv")
df = load_data(dataset_path)

print(df.shape)   # (48895, 16)
```

---

#### `display_dataset_info(df)`

Prints the number of rows and columns and lists every column name. Useful for a quick sanity check after loading.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `df` | `pandas.DataFrame` | Any DataFrame, typically the one returned by `load_data()` |

**Returns**  
`None` — output goes to the console only.

**Example**

```python
from src.data_loader import load_data, display_dataset_info

df = load_data("data/Airbnb_NYC.csv")
display_dataset_info(df)
```

**Sample output**

```
NYC Airbnb Dataset Information
----------------------------------------
Number of rows: 48895
Number of columns: 16

Column names:
- id
- name
- host_id
- host_name
- neighbourhood_group
- neighbourhood
- latitude
- longitude
- room_type
- price
- minimum_nights
- number_of_reviews
- last_review
- reviews_per_month
- calculated_host_listings_count
- availability_365
```

---

### `src/data_cleaning.py`

#### `clean_data(df)`

Applies a series of cleaning steps to the raw Airbnb DataFrame and returns a new, cleaned copy. **The original DataFrame is never modified.**

**Parameters**

| Name | Type | Description |
|---|---|---|
| `df` | `pandas.DataFrame` | Raw DataFrame, typically the one returned by `load_data()` |

**Returns**  
`pandas.DataFrame` — a cleaned copy with a reset integer index starting at 0.

**Raises**

| Exception | Condition |
|---|---|
| `TypeError` | `df` is not a pandas DataFrame |
| `ValueError` | One or more required columns are missing |

**Required columns**

`id`, `neighbourhood_group`, `neighbourhood`, `room_type`, `price`, `minimum_nights`, `availability_365`

**Example**

```python
from src.data_loader import load_data
from src.data_cleaning import clean_data

raw_df    = load_data("data/Airbnb_NYC.csv")
clean_df  = clean_data(raw_df)

print(f"Raw rows:     {len(raw_df)}")
print(f"Cleaned rows: {len(clean_df)}")
print(f"Removed:      {len(raw_df) - len(clean_df)}")
```

---

### Cleaning Rules Applied by `clean_data()`

The function applies seven cleaning steps in order. Each step is described below.

---

#### Step 1 — Strip whitespace from text columns

**Columns affected:** `name`, `host_name`, `neighbourhood_group`, `neighbourhood`, `room_type`

Leading and trailing spaces are removed with `.str.strip()`. This prevents values like `" Brooklyn"` and `"Brooklyn"` from being treated as two different groups in analysis.

```
Before: "  Brooklyn  "
After:  "Brooklyn"
```

---

#### Step 2 — Fill missing listing and host names

| Column | Missing value replaced with |
|---|---|
| `name` | `"Unknown listing"` |
| `host_name` | `"Unknown host"` |

A missing name does not disqualify a listing. These are optional fields, so `NaN` values are filled with a placeholder rather than dropping the row.

---

#### Step 3 — Drop rows missing essential information

Rows where any of the following columns are `NaN` are removed:

- `id`
- `neighbourhood_group`
- `neighbourhood`
- `room_type`

Without these fields a listing cannot be categorised or grouped in any meaningful way.

---

#### Step 4 — Convert numeric columns

The following columns are cast to numeric using `pd.to_numeric(..., errors="coerce")`:

- `price`
- `minimum_nights`
- `availability_365`

Any value that cannot be converted (e.g. a string like `"N/A"`) becomes `NaN` and is removed in the next step.

---

#### Step 5 — Remove rows with invalid numeric values

| Column | Valid range | Rows removed when |
|---|---|---|
| `price` | > 0 | zero, negative, or NaN |
| `minimum_nights` | ≥ 1 and whole number | less than 1 or fractional (e.g. 1.5) |
| `availability_365` | 0 – 365 and whole number | outside range or fractional |

> **Note:** `availability_365 = 0` is **valid** — it means the listing is blocked for the whole year but is still a real record in the dataset.

---

#### Step 6 — Handle optional review fields

| Situation | Action |
|---|---|
| `number_of_reviews = 0` and `reviews_per_month` is `NaN` | Set `reviews_per_month` to `0.0` |
| `reviews_per_month` is negative | Replace with `NaN` |
| `last_review` is `NaN` | **Preserved as-is** — a null date means the listing has no reviews yet, which is meaningful |

---

#### Step 7 — Remove duplicate records

1. **Exact duplicate rows** — if two rows are completely identical, the first is kept and the second is removed.
2. **Duplicate listing IDs** — if two rows share the same `id` but differ in other fields, the first occurrence is kept.

---

## Test File

**File:** `tests/test_task05_data_loading_cleaning.py`  
**Runner:** `pytest`  
**Total tests:** 51 ✅

### How to Run

From the project root directory:

```bash
python -m pytest tests/test_task05_data_loading_cleaning.py -v
```

To run all tests in the project:

```bash
python -m pytest tests/ -v
```

---

### Test Categories and Coverage

| # | Test Class | What it checks | Tests |
|---|---|---|---|
| 1 | `TestLoadData` | File not found, correct row count, Path object support, error message | 5 |
| 2 | `TestCleanDataInputValidation` | TypeError on non-DataFrame, ValueError on missing columns, error message content | 4 |
| 3 | `TestCleanDataReturnStructure` | Returns DataFrame, original not modified, columns unchanged, index reset to 0 | 4 |
| 4 | `TestCleanDataKeepsValidRow` | A fully valid row passes through unchanged | 2 |
| 5 | `TestCleanDataPriceRules` | Zero, negative, NaN prices removed; valid price kept; mixed batch | 5 |
| 6 | `TestCleanDataMinimumNightsRules` | Zero, negative, fractional values removed; 1 night kept | 4 |
| 7 | `TestCleanDataAvailabilityRules` | Negative and >365 removed; 0 and 365 kept; fractional removed | 5 |
| 8 | `TestCleanDataTextNormalisation` | Whitespace stripped; missing name/host_name filled with placeholder | 3 |
| 9 | `TestCleanDataMissingEssentials` | Rows missing neighbourhood_group or room_type removed | 2 |
| 10 | `TestCleanDataDuplicates` | Exact duplicates removed; duplicate ID keeps first; unique rows all kept | 3 |
| 11 | `TestCleanDataReviewFields` | Zero reviews → reviews_per_month = 0.0; null last_review preserved | 2 |
| 12 | `TestIntegrationLoadAndClean` | Load + clean real CSV — shape, no invalid prices, no duplicate IDs, required columns present | 7 |
| 13 | `TestDocumentation` | All public functions have docstrings mentioning Parameters and Returns | 5 |
| | **Total** | | **51** |

---

### Test Results

```
============================= test session starts ==============================
platform linux -- Python 3.13, pytest-9.2.0
collected 51 items

tests/test_task05_data_loading_cleaning.py::TestLoadData::test_error_message_contains_path PASSED
tests/test_task05_data_loading_cleaning.py::TestLoadData::test_load_correct_row_count PASSED
tests/test_task05_data_loading_cleaning.py::TestLoadData::test_load_path_object_accepted PASSED
tests/test_task05_data_loading_cleaning.py::TestLoadData::test_load_returns_dataframe PASSED
tests/test_task05_data_loading_cleaning.py::TestLoadData::test_missing_file_raises_file_not_found_error PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataInputValidation::test_dict_raises_type_error PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataInputValidation::test_error_message_names_missing_column PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataInputValidation::test_missing_required_column_raises_value_error PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataInputValidation::test_non_dataframe_raises_type_error PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataReturnStructure::test_does_not_modify_original PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataReturnStructure::test_index_is_reset PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataReturnStructure::test_output_columns_match_input_columns PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataReturnStructure::test_returns_dataframe PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataKeepsValidRow::test_valid_row_is_kept PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataKeepsValidRow::test_valid_row_price_preserved PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataPriceRules::test_mixed_prices_only_valid_kept PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataPriceRules::test_nan_price_row_is_removed PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataPriceRules::test_negative_price_row_is_removed PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataPriceRules::test_valid_price_row_is_kept PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataPriceRules::test_zero_price_row_is_removed PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataMinimumNightsRules::test_fractional_minimum_nights_is_removed PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataMinimumNightsRules::test_negative_minimum_nights_is_removed PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataMinimumNightsRules::test_valid_minimum_nights_kept PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataMinimumNightsRules::test_zero_minimum_nights_is_removed PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataAvailabilityRules::test_availability_365_is_valid PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataAvailabilityRules::test_availability_above_365_is_removed PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataAvailabilityRules::test_availability_below_zero_is_removed PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataAvailabilityRules::test_availability_zero_is_valid PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataAvailabilityRules::test_fractional_availability_is_removed PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataTextNormalisation::test_missing_host_name_filled_with_placeholder PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataTextNormalisation::test_missing_name_filled_with_placeholder PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataTextNormalisation::test_whitespace_stripped_from_neighbourhood_group PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataMissingEssentials::test_row_missing_neighbourhood_group_is_removed PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataMissingEssentials::test_row_missing_room_type_is_removed PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataDuplicates::test_duplicate_id_keeps_first PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataDuplicates::test_exact_duplicate_rows_removed PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataDuplicates::test_unique_rows_all_kept PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataReviewFields::test_missing_last_review_is_preserved PASSED
tests/test_task05_data_loading_cleaning.py::TestCleanDataReviewFields::test_zero_reviews_sets_reviews_per_month_to_zero PASSED
tests/test_task05_data_loading_cleaning.py::TestIntegrationLoadAndClean::test_availability_in_range_after_cleaning PASSED
tests/test_task05_data_loading_cleaning.py::TestIntegrationLoadAndClean::test_cleaned_df_has_rows PASSED
tests/test_task05_data_loading_cleaning.py::TestIntegrationLoadAndClean::test_cleaned_df_is_dataframe PASSED
tests/test_task05_data_loading_cleaning.py::TestIntegrationLoadAndClean::test_cleaned_df_smaller_than_raw PASSED
tests/test_task05_data_loading_cleaning.py::TestIntegrationLoadAndClean::test_no_duplicate_ids_after_cleaning PASSED
tests/test_task05_data_loading_cleaning.py::TestIntegrationLoadAndClean::test_no_invalid_prices_after_cleaning PASSED
tests/test_task05_data_loading_cleaning.py::TestIntegrationLoadAndClean::test_required_columns_present PASSED
tests/test_task05_data_loading_cleaning.py::TestDocumentation::test_clean_data_docstring_mentions_parameters PASSED
tests/test_task05_data_loading_cleaning.py::TestDocumentation::test_clean_data_docstring_mentions_returns PASSED
tests/test_task05_data_loading_cleaning.py::TestDocumentation::test_clean_data_has_docstring PASSED
tests/test_task05_data_loading_cleaning.py::TestDocumentation::test_display_dataset_info_has_docstring PASSED
tests/test_task05_data_loading_cleaning.py::TestDocumentation::test_load_data_has_docstring PASSED

==================== 51 passed, 7 subtests passed in 1.11s ====================
```

---

## Acceptance Criteria — Status

| Criterion | Status |
|---|---|
| Data-loading functionality is tested | ✅ 5 unit tests for `load_data()` |
| Data-cleaning functionality is tested | ✅ 39 unit + integration tests for `clean_data()` |
| Functions return expected outputs | ✅ Return type and structure verified |
| Data cleaning rules are verified | ✅ Each of the 7 cleaning steps has dedicated tests |
| Functions include clear documentation | ✅ Docstrings verified by test class `TestDocumentation` |
| Testing results are recorded | ✅ Full output recorded in this document |
| The code executes without errors | ✅ 51/51 tests pass |

---

## Files Changed in This Task

| File | Type | Description |
|---|---|---|
| `tests/test_task05_data_loading_cleaning.py` | New | 51 unit and integration tests |
| `docs/task05-data-loading-cleaning.md` | New | This documentation file |
| `.gitignore` | New | Excludes `__pycache__`, `.pytest_cache`, IDE folders, large CSV files |
