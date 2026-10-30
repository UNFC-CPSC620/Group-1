# TASK-15: Overall Airbnb Reviews — Testing & Documentation

**Course:** CPSC 620 – Agile Software Development  
**Project:** NYC Airbnb Data Summary Tool  
**Issue:** [#21](https://github.com/UNFC-CPSC620/Group-1/issues/21)  
**Related User Story:** US-05 – NYC Airbnb Review Analysis ([#20](https://github.com/UNFC-CPSC620/Group-1/issues/20))  
**Branch:** `feature/task-15-review-analysis`

---

## Overview

This document covers the implementation, testing, and documentation of the overall review analysis module for the NYC Airbnb Data Summary Tool.

The module calculates review statistics across Airbnb listings using two dataset columns:

| Column | Description |
|---|---|
| `number_of_reviews` | Total number of reviews received by each listing |
| `reviews_per_month` | Average monthly review activity for each listing |

The analysis provides an overview of review activity, identifies listings with no reviews, and handles missing or invalid values to ensure reliable results.

---

## Module Documentation

### `src/review_analysis.py`

#### `analyze_overall_reviews(df)`

Calculates overall review statistics for NYC Airbnb listings and returns the results as a reusable Python dictionary.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `df` | `pandas.DataFrame` | Dataset containing `number_of_reviews` and `reviews_per_month` |

**Returns**

`dict` — a dictionary containing:

| Key | Description |
|---|---|
| `total_listings` | Total number of listings in the input DataFrame |
| `total_reviews` | Sum of valid review counts |
| `valid_review_listing_count` | Number of listings with valid review counts |
| `average_reviews_per_listing` | Average reviews per listing with a valid review count |
| `zero_review_listings` | Number of listings with zero reviews |
| `average_reviews_per_month` | Average monthly review activity using valid values |
| `invalid_review_counts` | Number of missing or invalid total review counts |
| `invalid_monthly_reviews` | Number of missing or invalid monthly review values |

**Raises**

- `TypeError` — if the input is not a pandas DataFrame.
- `KeyError` — if one or more required columns are missing.

**Example**

```python
from pathlib import Path

from src.data_loader import load_data
from src.review_analysis import analyze_overall_reviews

dataset_path = Path("data/Airbnb_NYC.csv")
df = load_data(dataset_path)

results = analyze_overall_reviews(df)

print(results)
```

---

## Data Handling and Validation

The function applies validation rules before calculating statistics.

### 1. Input validation

- Confirms that the input is a pandas DataFrame.
- Checks that both required columns are present.
- Raises an appropriate exception when validation fails.

### 2. Numeric conversion

Both review columns are converted using:

```python
pd.to_numeric(errors="coerce")
```

Values that cannot be converted become `NaN`.

### 3. Valid review counts

For `number_of_reviews`, valid values must:

- Be numeric and finite.
- Be greater than or equal to zero.
- Be whole numbers (integers).

Negative, missing, non-numeric, infinite, and fractional values are excluded.

### 4. Valid monthly review activity

For `reviews_per_month`, valid values must:

- Be numeric and finite.
- Be greater than or equal to zero.

Missing, negative, non-numeric, and infinite values are excluded.

### 5. Statistical calculations

- Total reviews are calculated using valid review counts only.
- Average reviews per listing uses the number of listings with valid review counts as its denominator.
- Listings with zero reviews are counted among valid review counts.
- Average monthly review activity uses only valid monthly values.
- Invalid values are counted separately for each review column.

**Note:** The original DataFrame is never modified. All calculations use converted Series and filtered values.

---

## Test File

**File:** `tests/test_task15_review_analysis.py`  
**Module under test:** `src/review_analysis.py`  
**Runner:** `pytest`  
**Total tests:** 11

### How to Run

From the project root directory:

```bash
python3 -m pytest tests/test_task15_review_analysis.py -v
```

To run the complete project test suite:

```bash
python3 -m pytest -v
```

### Test Categories and Coverage

| # | Test | What it checks |
|---|---|---|
| 1 | Overall statistics | Correct calculation of review statistics |
| 2 | Zero-review listings | Correct identification and counting of listings with zero reviews |
| 3 | Missing and negative values | Invalid review counts are excluded |
| 4 | Non-numeric values | Non-numeric review counts are excluded |
| 5 | Infinite values | Infinite review counts are excluded |
| 6 | Fractional review counts | Fractional total review counts are excluded |
| 7 | Invalid monthly values | Invalid monthly review activity is excluded |
| 8 | DataFrame preservation | Original DataFrame remains unchanged |
| 9 | Missing columns | Raises `KeyError` when required columns are missing |
| 10 | Invalid input type | Raises `TypeError` for non-DataFrame input |
| 11 | Empty DataFrame | Handles empty input without errors |

---

## Test Results

The dedicated TASK-15 test suite was executed successfully.

```text
11 passed
```

The complete project test suite was also executed successfully:

```text
101 passed, 18 subtests passed
```

No test failures were reported in these executions.

---

## Dataset Analysis Results

The function was executed using the NYC Airbnb dataset (`data/Airbnb_NYC.csv`).

The analysis returned the following results:

| Metric | Result |
|---|---:|
| Total listings | 42,336 |
| Total reviews | 996,893 |
| Valid review listings | 42,336 |
| Average reviews per listing | 23.55 |
| Listings with zero reviews | 8,732 |
| Average reviews per month | 1.38 |
| Invalid review counts | 0 |
| Invalid monthly reviews | 8,956 |

These results reflect the current dataset and the validation rules implemented in the module.

---

## Acceptance Criteria — Status

| Criterion | Status |
|---|---|
| Total reviews are calculated correctly | ✅ Implemented and tested |
| Average reviews per listing are calculated correctly | ✅ Uses valid review listings as denominator |
| Listings with zero reviews are identified | ✅ Implemented and tested |
| Average monthly review activity is calculated | ✅ Implemented and tested |
| Missing or invalid review values are handled | ✅ Implemented and tested |
| Functions return reusable results | ✅ Returns a structured dictionary |
| Code includes clear documentation | ✅ Function docstring and this document |
| Functions execute without errors | ✅ 11 dedicated tests passed |

---

## Files Changed in This Task

| File | Type | Description |
|---|---|---|
| `src/review_analysis.py` | New | Reusable overall Airbnb review analysis function |
| `tests/test_task15_review_analysis.py` | New | 11 unit tests covering calculations, validation, and edge cases |
| `docs/task15-review-analysis.md` | New | Implementation, testing, and results documentation |

---

**Integration note:** Final integration verification should be performed after the related review-analysis tasks are completed and merged into the main branch.