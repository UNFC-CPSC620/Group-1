# TASK-11 â€” Neighbourhood Analysis Testing Report

**Project:** NYC Airbnb Data Summary Tool
**Course:** CPSC620
**Issue:** #15
**Related user story:** US-03 (#12)
**Implementation pull requests:** #25 (price and neighbourhood analysis) and #26 (neighbourhood-group distribution)
**Verification date:** October 27, 2026

## Objective

Verify listing counts, percentage distributions, average prices, top-neighbourhood rankings, and handling of missing or invalid values. Record repeatable test instructions and representative results.

## Test setup

The unit tests use small in-memory Pandas DataFrames so expected results are deterministic and do not depend on the full CSV file. The verification run used the implementation and test files from PRs #25 and #26 in a temporary worktree. Those PRs were open and unmerged at the time, so these results describe the combined feature-branch files; they do not claim that the current `main` branch contains those modules.

The test files are:

- `tests/test_neighbourhood_analysis.py` â€” 8 tests for valid prices, averages, rankings, input validation, return types, and input immutability.
- `tests/test_neighbourhood_group_analysis.py` â€” 7 tests for counts, percentages, missing labels, empty data, and input validation.
- `tests/test_neighbourhood_normalization.py` â€” 1 regression test for case-insensitive neighbourhood names.

## Run the tests in Windows PowerShell

Run these commands in the terminal from the package root. Keep this Markdown report in `docs/NEIGHBOURHOOD_TEST_REPORT.md`; do not paste the report text or its headings and tables into PowerShell.

```powershell
Set-Location <path-to-task11-deliverable>
py -m unittest discover -s tests -v
```

Or run the supplied script:

```powershell
./RUN_TESTS.ps1
```

## Automated test results

The verification command `python -m unittest discover -s tests -v` completed successfully.

| Test suite | Tests | Result |
|---|---:|---|
| Neighbourhood price analysis | 8 | PASS |
| Neighbourhood-group analysis | 7 | PASS |
| Neighbourhood name normalization | 1 | PASS |
| **Total** | **16** | **PASS** |

Recorded output: `Ran 16 tests in 0.075s â€” OK`.

## Dataset summary results

The following full-dataset figures are the sample outputs recorded by the implementation pull requests. The isolated 16-test run above used deterministic fixtures and did not reload the 6.2 MB CSV.

### Listings by neighbourhood group

| Neighbourhood group | Listings | Percentage |
|---|---:|---:|
| Manhattan | 18,764 | 44.32% |
| Brooklyn | 17,396 | 41.09% |
| Queens | 4,903 | 11.58% |
| Bronx | 948 | 2.24% |
| Staten Island | 325 | 0.77% |
| **Total** | **42,336** | **100.00%** |

The group-count function includes records with a valid group label regardless of price. Missing or blank group labels are excluded from both the counts and percentage denominator.

### Average prices by neighbourhood group

| Neighbourhood group | Average price | Valid-price listings |
|---|---:|---:|
| Manhattan | $198.60 | 18,669 |
| Brooklyn | $124.62 | 17,309 |
| Staten Island | $115.70 | 324 |
| Queens | $100.73 | 4,876 |
| Bronx | $87.91 | 941 |

Price summaries exclude missing, nonnumeric, non-finite, zero, and negative prices. The implementation pull request recorded 42,119 valid-price rows and 217 excluded rows.

### Top 10 neighbourhoods by valid-price listings

| Rank | Neighbourhood | Listings |
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

These rankings count rows with valid positive prices, matching the price-analysis function's documented policy.

## Missing and invalid values

The unit tests verify that:

- Missing required columns raise `ValueError`; non-DataFrame input raises `TypeError`.
- Missing or blank group and neighbourhood names are excluded from group summaries.
- Nonnumeric, missing, infinite, zero, and negative prices are excluded from price calculations.
- Invalid `top_n` values raise `ValueError`.
- Empty inputs return an empty DataFrame with the expected output columns.
- Analysis leaves the caller's DataFrame unchanged.

## Regression finding

Case variants such as `Tribeca` / `tribeca` and `Red Hook` / `red hook` must not be counted as separate neighbourhoods. The normalization regression test verifies merged counts and averages while retaining a canonical display spelling.

## Acceptance criteria

| Criterion | Result |
|---|---|
| Listing counts verified | PASS |
| Percentage calculations verified | PASS |
| Average prices verified | PASS |
| Top-neighbourhood ranking verified | PASS |
| Missing and invalid values handled | PASS |
| Expected DataFrame results verified | PASS |
| Results and repeatable PowerShell commands documented | PASS |
| Automated tests execute without errors in the combined feature worktree | PASS |

## Integration note

At verification time, PRs #25 and #26 were not merged into `main`. Run the same command again after those implementation and test changes are integrated to confirm the final combined repository state.

## Conclusion

All 16 unit tests passed against the combined neighbourhood-analysis feature files. The report distinguishes fixture-based unit-test results from the full-dataset sample summaries and provides PowerShell commands separately from the Markdown content.
