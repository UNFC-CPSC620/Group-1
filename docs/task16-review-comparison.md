# TASK-16: Compare Review Activity by Room Type and Neighbourhood

## 1. Overview

This task develops reusable Python functions to compare Airbnb review activity across different room types and NYC neighbourhood groups.

The analysis supports US-05: NYC Airbnb Review Analysis.

## 2. Implementation

The module `src/review_comparison.py` contains two functions:

### 2.1 Compare Reviews by Room Type

Function: `compare_reviews_by_room_type(df)`

Groups Airbnb listings by `room_type` and calculates:

- Average total reviews (`average_reviews`).
- Average monthly reviews (`average_reviews_per_month`).
- Number of listings (`listing_count`).

Room type names are normalized to avoid duplicate categories caused by inconsistent capitalization or whitespace.

### 2.2 Compare Reviews by Neighbourhood

Function: `compare_reviews_by_neighbourhood(df)`

Groups Airbnb listings by `neighbourhood_group` and calculates:

- Average total reviews (`average_reviews`).
- Average monthly reviews (`average_reviews_per_month`).
- Number of listings (`listing_count`).

Neighbourhood group names are normalized for consistent grouping.

## 3. Data Validation and Handling

Both functions:

- Verify that the input is a Pandas DataFrame. A `TypeError` is raised when the input has an invalid type.
- Verify that all required columns are available.
- Convert review values to numeric format.
- Exclude missing, non-numeric, negative, and non-finite review values from averages.
- Require `number_of_reviews` to contain non-negative integer values. Fractional review counts are excluded from average review calculations.
- Allow decimal values for `reviews_per_month`, provided they are finite and non-negative.
- Handle Pandas nullable numeric types, including `Int64` and `Float64`.
- Exclude listings with missing or blank grouping categories.
- Work with a copy of the input DataFrame to preserve the original data.

The `listing_count` aggregation represents the number of listings in each valid group, while review averages use valid review values.

Results are returned as reusable Pandas DataFrames.

## 4. Testing

A dedicated test file is available:

`tests/test_task16_review_comparison.py`

Eleven unit tests verify:

1. Review comparison by room type.
2. Review comparison by neighbourhood group.
3. Handling of missing values.
4. Handling of invalid review values.
5. Exclusion of fractional review counts by room type.
6. Exclusion of fractional review counts by neighbourhood.
7. Handling of Pandas nullable numeric columns (`Int64` and `Float64`).
8. Preservation of the original DataFrame.
9. Validation of required columns.
10. Rejection of non-DataFrame inputs for room-type comparison.
11. Rejection of non-DataFrame inputs for neighbourhood comparison.

### Test Results

- Dedicated TASK-16 tests: 11 passed.
- Full project test suite: 101 passed.
- Additional subtests: 18 passed.
- No test failures.

## 5. Files

| File | Description |
|---|---|
| `src/review_comparison.py` | Reusable review comparison functions. |
| `tests/test_task16_review_comparison.py` | Eleven unit tests for TASK-16. |
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
| Fractional review counts excluded from average calculations | Implemented and tested |
| Nullable Pandas numeric values handled appropriately | Implemented and tested |
| Non-DataFrame inputs rejected with TypeError | Implemented and tested |
| Results returned as Pandas DataFrames | Implemented and tested |
| Original DataFrame remains unchanged | Implemented and tested |
| Functions documented and reusable | Implemented |
| Code executes without errors | Verified |

## 7. Integration Note

Final integration should be verified after the related review-analysis tasks have been reviewed and merged into the main branch.
