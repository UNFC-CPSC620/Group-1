# TASK-11 — Neighbourhood Analysis Testing Report

**Project:** NYC Airbnb Data Summary Tool

**Course:** CPSC620

**Issue:** #15

**Related User Story:** US-03 (#12)

**Related Pull Requests:** #25 and #26

**Test Date:** October 27, 2026

## 1. Objective

Validate and document the neighbourhood analysis functions, including listing counts, percentage distributions, average prices, top neighbourhood rankings, missing and invalid value handling, and code reliability.

## 2. Testing Environment

- Language: Python

- Library: Pandas

- Testing framework: unittest

- Dataset: `data/Airbnb_NYC.csv`

- Total dataset records: 42,336

- Testing performed in an isolated Git worktree using the implementation modules from PR #25 and PR #26.

## 3. Automated Testing Results

All 16 automated tests passed successfully.
| Test Suite | Tests | Result |
|---|---:|---|
| Neighbourhood price analysis | 8 | PASS |
| Neighbourhood group analysis | 7 | PASS |
| Neighbourhood name normalization | 1 | PASS |
| **Total** | **16** | **PASS** |

Execution command:

`py -m unittest discover -s tests -v`

Recorded result:

`Ran 16 tests in 0.073s — OK`

## 4. Neighbourhood Group Distribution
| Neighbourhood Group | Listing Count | Percentage |
|---|---:|---:|
| Manhattan | 18,764 | 44.32% |
| Brooklyn | 17,396 | 41.09% |
| Queens | 4,903 | 11.58% |
| Bronx | 948 | 2.24% |
| Staten Island | 325 | 0.77% |
| **Total** | **42,336** | **100.00%** |

All listings were included in the neighbourhood group distribution.

## 5. Average Prices by Neighbourhood Group
| Neighbourhood Group | Average Price | Valid-Price Listings |
|---|---:|---:|
| Manhattan | $198.60 | 18,669 |
| Brooklyn | $124.62 | 17,309 |
| Staten Island | $115.70 | 324 |
| Queens | $100.73 | 4,876 |
| Bronx | $87.91 | 941 |

The price analysis retained 42,119 records with valid, positive, finite prices and excluded 217 records from price calculations.

## 6. Top 10 Neighbourhoods by Valid-Price Listings
| Rank | Neighbourhood | Listing Count |
|---:|---|---:|
| 1 | Williamsburg | 3,376 |
| 2 | Bedford-Stuyvesant | 3,177 |
| 3 | Harlem | 2,304 |
| 4 | Bushwick | 2,116 |
| 5 | Upper West Side | 1,723 |
| 6 | Hell's Kitchen | 1,662 |
| 7 | East Village | 1,606 |
| 8 | Upper East Side | 1,542 |
| 9 | Crown Heights | 1,335 |
| 10 | Midtown | 1,332 |

These rankings use valid-price listings, rather than every raw listing.

## 7. Missing and Invalid Value Handling

The automated tests cover:

- Missing required columns.

- Non-DataFrame inputs.

- Missing or empty neighbourhood group values.

- Invalid and non-positive prices.

- Invalid top-N ranking parameters.

- Empty DataFrames.

- Preservation of the original input DataFrame.

All corresponding automated tests passed.

## 8. Defect Identified and Corrected

**Issue:** Neighbourhood names with different capitalization were treated as separate neighbourhoods.

Examples identified in the dataset:

- `Tribeca` and `tribeca`

- `Red Hook` and `red hook`

**Correction:** Implemented case-insensitive neighbourhood name normalization while preserving the most frequently occurring spelling.

### Results After Correction
| Neighbourhood | Valid-Price Listings | Average Price |
|---|---:|---:|
| Tribeca | 151 | $504.65 |
| Red Hook | 70 | $144.93 |

The normalization check passed.

A dedicated regression test was implemented in `tests/test_neighbourhood_normalization.py` and published through PR #25.

## 9. Acceptance Criteria Verification
| Acceptance Criterion | Result |
|---|---|
| Listing counts verified | PASS |
| Percentage calculations accurate | PASS |
| Average price calculations tested | PASS |
| Top neighbourhood rankings tested | PASS |
| Missing and invalid values handled | PASS |
| Expected DataFrame outputs verified | PASS |
| Testing results documented | PASS |
| Automated tests execute without errors | PASS |

## 10. Integration and Review Notes

The 16-test run was performed in an isolated testing worktree containing the two modules under review and the regression correction.

At the time of testing, PR #25 and PR #26 were not yet merged into `main`. Therefore, this result documents successful testing of their combined working copies, not a completed integration into the main branch.

The combined test suite should be rerun after both pull requests have been merged.

## 11. Conclusion

The neighbourhood analysis implementations passed 16 automated tests and produced the documented results on the NYC Airbnb dataset.

Testing also identified a capitalization-related data quality defect, which was corrected and covered by a regression test.

The functions are ready for code review and final integration, subject to approval and merging of the related pull requests.
