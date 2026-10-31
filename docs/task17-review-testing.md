# TASK-17: Review Analysis Testing and Documentation

**Project:** NYC Airbnb Data Summary Tool  
**Course:** CPSC620 – Agile Software Development  
**Related User Story:** US-05 – Review Analysis  
**Related Tasks:** TASK-15 and TASK-16  
**Issue:** #23

## 1. Objective

The objective of TASK-17 is to test, validate, and document the review analysis functionality developed in TASK-15 and TASK-16.

This task verifies that overall review statistics and grouped review comparisons produce accurate, consistent results while handling invalid or missing data appropriately.

The testing process also ensures that the existing functionality of the project remains unaffected.

## 2. Modules Reviewed

The following Python modules were reviewed:

| Module | Function | Description |
|---|---|---|
| `src/review_analysis.py` | `analyze_overall_reviews()` | Calculates overall review statistics. |
| `src/review_comparison.py` | `compare_reviews_by_room_type()` | Compares review statistics across room types. |
| `src/review_comparison.py` | `compare_reviews_by_neighbourhood()` | Compares review statistics across neighbourhood groups. |

The existing implementations were reused without modifying their functionality.

## 3. Testing Approach

Testing was performed using Python, Pandas, and Pytest.

The integration tests were implemented in:

`tests/test_task17_review_integration.py`

A controlled sample DataFrame was used to verify expected calculations and relationships between the review analysis modules.

The sample dataset included five Airbnb listings with different room types, neighbourhood groups, review counts, and monthly review averages.

Additional test cases covered missing values, negative values, empty datasets, and preservation of the original input DataFrame.

## 4. Integration Test Cases

Seven integration tests were implemented.

| Test | Description | Result |
|---|---|---|
| `test_overall_review_statistics` | Verifies total reviews, averages, and zero-review listings. | PASSED |
| `test_room_type_review_summary` | Verifies review summaries grouped by room type. | PASSED |
| `test_neighbourhood_review_summary` | Verifies review summaries grouped by neighbourhood group. | PASSED |
| `test_review_totals_are_consistent_across_modules` | Confirms consistency between overall and grouped review totals. | PASSED |
| `test_invalid_review_values_across_modules` | Verifies handling of negative and missing review values. | PASSED |
| `test_integration_does_not_modify_original_data` | Confirms that analysis functions preserve the original DataFrame. | PASSED |
| `test_empty_dataset_across_modules` | Verifies that the modules handle empty datasets. | PASSED |

**Integration testing result: 7 passed, 0 failed.**

## 5. Sample Input Data

The following controlled dataset was used for integration testing:

| Room Type | Neighbourhood Group | Number of Reviews | Reviews per Month |
|---|---|---:|---:|
| Private room | Brooklyn | 10 | 1.0 |
| Entire home/apt | Manhattan | 20 | 2.0 |
| Private room | Brooklyn | 0 | 0.0 |
| Shared room | Queens | 30 | 3.0 |
| Entire home/apt | Manhattan | 40 | 4.0 |

## 6. Expected and Validated Results

### 6.1 Overall Review Statistics

The following results were verified using the controlled dataset:

| Metric | Validated Value |
|---|---:|
| Total listings | 5 |
| Total reviews | 100 |
| Average reviews per listing | 20.0 |
| Listings with zero reviews | 1 |
| Average reviews per month | 2.0 |

These values confirm that the overall review analysis function calculates the expected statistics.

### 6.2 Review Analysis by Room Type

The integration tests verified the following results for private rooms:

| Metric | Validated Value |
|---|---:|
| Listing count | 2 |
| Average reviews | 5.0 |
| Average reviews per month | 0.5 |

The grouped listing counts were also verified to total five listings.

### 6.3 Review Analysis by Neighbourhood Group

The integration tests verified the following results for Brooklyn:

| Metric | Validated Value |
|---|---:|
| Listing count | 2 |
| Average reviews | 5.0 |
| Average reviews per month | 0.5 |

The grouped listing counts were also verified to total five listings.

### 6.4 Cross-Module Consistency

The integration tests confirmed that, for the controlled dataset containing valid review counts, the weighted totals calculated from room-type and neighbourhood-group summaries matched the overall total of 100 reviews.

This verifies consistency between the analysis functions for the tested scenario.

## 7. Missing and Invalid Data

An additional dataset containing valid, negative, and missing review values was used.

The tests confirmed the following:

- Valid review counts were included in the total.
- Negative and missing review counts were identified as invalid.
- Negative and missing monthly review values were identified as invalid.
- Grouped listing counts included all listings belonging to valid categories, even when their review values were invalid.
- The functions completed successfully without modifying the original input DataFrame.

For the invalid-data test case, the validated results included:

| Metric | Validated Value |
|---|---:|
| Total valid reviews | 10 |
| Invalid review counts | 2 |
| Invalid monthly review values | 2 |
| Total listings in room-type groups | 3 |
| Total listings in neighbourhood groups | 3 |

## 8. Code and Documentation Review

The review analysis modules were exercised through their public functions without requiring modifications to the existing implementation.

The integration test file uses descriptive test names, short docstrings, reusable sample data, and explicit assertions to make the expected behaviour understandable.

Existing unit tests from TASK-15 and TASK-16 provide additional coverage for input validation, invalid values, nullable Pandas columns, and preservation of input data.

The TASK-15 and TASK-16 documentation files are also available in the project:

- `docs/task15-review-analysis.md`
- `docs/task16-review-comparison.md`

Together, these documents and the TASK-17 integration tests support the review analysis functionality.

## 9. Test Execution

### 9.1 Integration Tests

The integration tests were executed using:

```bash
/usr/local/bin/python3 -m pytest tests/test_task17_review_integration.py -v
```

**Final result:**

```text
7 passed
```

### 9.2 Complete Project Test Suite

The complete project test suite was executed using:

```bash
/usr/local/bin/python3 -m pytest -v
```

**Final result:**

```text
187 passed, 18 subtests passed in 1.03s
```

All collected tests passed successfully.

The results indicate that the new integration tests did not introduce failures in the existing project test suite.

## 10. Acceptance Criteria Verification

| Acceptance Criterion | Status |
|---|---|
| Test total and average review calculations | Completed |
| Verify listings with zero reviews | Completed |
| Test average monthly review calculations | Completed |
| Validate review summaries by room type | Completed |
| Verify review summaries by neighbourhood group | Completed |
| Test missing and invalid values | Completed |
| Review code readability and documentation | Completed |
| Record testing results and sample outputs | Completed |
| Confirm execution without errors | Completed |

## 11. Conclusion

TASK-17 successfully validated the integration of the review analysis functionality developed in TASK-15 and TASK-16.

All seven integration tests passed, confirming the expected calculations, grouped comparisons, invalid-data handling, and preservation of input data for the tested scenarios.

The complete project test suite also passed, with 187 successful tests and 18 successful subtests.

The review analysis functionality is therefore ready for team review through the GitHub pull request process.