# TASK-16: Compare Review Activity by Room Type and Neighbourhood

## 1. Overview

This task develops reusable Python functions to compare Airbnb review
activity across different room types and NYC neighbourhood groups.

The analysis supports US-05: NYC Airbnb Review Analysis.

## 2. Implementation

A new module, `src/review_comparison.py`, was created with two functions:

### 2.1 Compare Reviews by Room Type

Function: `compare_reviews_by_room_type(df)`

Groups Airbnb listings by `room_type` and calculates:

- Average total reviews (`average_reviews`).
- Average monthly reviews (`average_reviews_per_month`).
- Number of listings (`listing_count`).

Room type names are normalized to avoid duplicate categories caused
by inconsistent capitalization or whitespace.

### 2.2 Compare Reviews by Neighbourhood

Function: `compare_reviews_by_neighbourhood(df)`

Groups Airbnb listings by `neighbourhood_group` and calculates:

- Average total reviews (`average_reviews`).
- Average monthly reviews (`average_reviews_per_month`).
- Number of listings (`listing_count`).

Neighbourhood group names are normalized for consistent grouping.

## 3. Data Validation and Handling

Both functions:

- Verify that all required columns are available.
- Convert review values to numeric format.
- Handle missing and non-numeric values.
- Exclude negative and non-finite review values from averages.
- Exclude listings with missing or blank grouping categories.
- Work with a copy of the input DataFrame to preserve the original data.

Results are returned as reusable Pandas DataFrames.

## 4. Testing

A dedicated test file was created:

`tests/test_task16_review_comparison.py`

Six unit tests were implemented to verify:

1. Review comparison by room type.
2. Review comparison by neighbourhood group.
3. Handling of missing values.
4. Handling of invalid review values.
5. Preservation of the original DataFrame.
6. Validation of required columns.

### Test Results

- Dedicated TASK-16 tests: 6 passed.
- Full project test suite: 96 passed.
- Additional subtests: 18 passed.
- No test failures.

## 5. Files Created

| File | Description |
|---|---|
| `src/review_comparison.py` | Reusable review comparison functions. |
| `tests/test_task16_review_comparison.py` | Six unit tests for TASK-16. |
| `docs/task16-review-comparison.md` | Implementation and testing documentation. |

## 6. Acceptance Criteria Status

| Acceptance Criterion | Status |
|---|---|
| Listings correctly grouped by room type | Implemented and tested |
| Average review counts calculated by room type | Implemented and tested |
| Listings correctly grouped by neighbourhood group | Implemented and tested |
| Average review counts calculated by neighbourhood group | Implemented and tested |
| Monthly review activity compared correctly | Implemented and tested |
| Missing and invalid values handled appropriately | Implemented and tested |
| Results returned as Pandas DataFrames | Implemented and tested |
| Functions documented and reusable | Implemented |
| Code executes without errors | Verified |

## 7. Integration Note

Final integration should be verified after the related review-analysis
tasks have been reviewed and merged into the main branch.