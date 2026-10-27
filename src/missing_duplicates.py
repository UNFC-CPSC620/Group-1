
"""
NYC Airbnb Data Quality Analysis
--------------------------------
Course: CPSC620
Project: NYC Airbnb Data Summary Tool
Task: TASK-02 / Issue #3

Reusable Pandas functions for identifying missing values
and duplicate records in the NYC Airbnb dataset.
"""

from pathlib import Path

import pandas as pd


def _validate_dataframe(df):
    """Ensure that the input is a Pandas DataFrame."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")


def missing_values_report(df):
    """
    Calculate missing values for every dataset column.

    Missing values include NaN, None, pd.NA, and blank
    or whitespace-only strings.

    Parameters
    ----------
    df : pandas.DataFrame
        Input Airbnb dataset.

    Returns
    -------
    pandas.DataFrame
        Columns:
        - column
        - missing_count
        - missing_percentage

        Column order matches the original dataset.
    """
    _validate_dataframe(df)

    results = []
    total_rows = len(df)

    for column in df.columns:
        series = df[column]

        missing_count = int(series.isna().sum())

        # Count blank strings as missing values.
        if (
            pd.api.types.is_object_dtype(series.dtype)
            or pd.api.types.is_string_dtype(series.dtype)
        ):
            blank_mask = (
                series.astype("string")
                .str.strip()
                .eq("")
            )

            missing_count += int(blank_mask.sum())

        percentage = (
            round(missing_count / total_rows * 100, 2)
            if total_rows > 0
            else 0.0
        )

        results.append({
            "column": column,
            "missing_count": missing_count,
            "missing_percentage": percentage,
        })

    return pd.DataFrame(
        results,
        columns=[
            "column",
            "missing_count",
            "missing_percentage",
        ],
    )


def find_duplicate_rows(df):
    """
    Identify all rows belonging to exact duplicate groups.

    Parameters
    ----------
    df : pandas.DataFrame
        Input Airbnb dataset.

    Returns
    -------
    pandas.DataFrame
        Copy of all rows involved in exact duplication,
        including their first occurrence.

    Notes
    -----
    Duplicate detection considers all columns.
    The original dataset is not modified.
    """
    _validate_dataframe(df)

    duplicate_mask = df.duplicated(
        keep=False
    )

    return df.loc[duplicate_mask].copy()


def duplicate_summary(df, id_column="id"):
    """
    Summarize duplicate records and repeated listing IDs.

    Parameters
    ----------
    df : pandas.DataFrame
        Input Airbnb dataset.
    id_column : str, default="id"
        Listing identifier column.

    Returns
    -------
    pandas.DataFrame
        Columns:
        - metric
        - count

    Notes
    -----
    Extra duplicate rows exclude the first occurrence.
    Missing IDs are excluded from duplicate-ID counts.
    """
    _validate_dataframe(df)

    exact_duplicate_count = int(
        df.duplicated(keep="first").sum()
    )

    all_duplicate_rows = int(
        df.duplicated(keep=False).sum()
    )

    results = [
        {
            "metric": "total_rows",
            "count": len(df),
        },
        {
            "metric": "extra_duplicate_rows",
            "count": exact_duplicate_count,
        },
        {
            "metric": "rows_in_duplicate_groups",
            "count": all_duplicate_rows,
        },
    ]

    if id_column in df.columns:
        valid_ids = df[id_column].dropna()

        repeated_ids = int(
            valid_ids.duplicated(keep="first").sum()
        )

        results.append({
            "metric": "extra_duplicate_ids",
            "count": repeated_ids,
        })

    return pd.DataFrame(
        results,
        columns=["metric", "count"],
    )


if __name__ == "__main__":
    dataset_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "Airbnb_NYC.csv"
    )

    df = pd.read_csv(dataset_path)

    print("\nNYC AIRBNB DATA QUALITY REPORT")
    print("=" * 45)

    print("\n1. MISSING VALUES")
    print(missing_values_report(df).to_string(index=False))

    print("\n2. DUPLICATE SUMMARY")
    print(duplicate_summary(df).to_string(index=False))

    print("\n3. DUPLICATE ROW PREVIEW")
    duplicates = find_duplicate_rows(df)

    if duplicates.empty:
        print("No exact duplicate rows found.")
    else:
        print(duplicates.head(10).to_string(index=False))

    print("\nAnalysis completed successfully.")
