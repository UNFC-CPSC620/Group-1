# =============================================================================
# neighbourhood_availability.py
# -----------------------------------------------------------------------------
# TASK-13: Compare Availability by Neighbourhood Group
#
# This module compares Airbnb listing availability across the five NYC
# neighbourhood groups (Bronx, Brooklyn, Manhattan, Queens, Staten Island).
# It builds on the overall availability analysis from TASK-12 by breaking
# the data down geographically.
#
# Author   : Alejandro (Kvothep)
# Issue    : #18
# Sprint   : Sprint 1
# =============================================================================

import pandas as pd


def compare_availability_by_neighbourhood(df):
    """
    Compare average availability across NYC neighbourhood groups.

    This function groups listings by `neighbourhood_group` and computes
    descriptive statistics for `availability_365` in each group. Only
    values in the valid range [0, 365] are used for statistics. The
    original DataFrame is never modified.

    How it works
    ------------
    1. Creates a working copy of the DataFrame
    2. Strips whitespace and title-cases neighbourhood_group values
    3. Converts availability_365 to numeric (handles string values)
    4. Filters out invalid values outside [0, 365]
    5. Groups by neighbourhood_group and computes mean, median, and count
    6. Sorts results from highest to lowest average availability
    7. Prints a formatted summary table to the console

    Parameters
    ----------
    df : pandas.DataFrame
        The NYC Airbnb dataset. Must contain:
        - `neighbourhood_group` : string column (e.g. 'Brooklyn', 'Manhattan')
        - `availability_365`    : numeric column (days available per year)

    Returns
    -------
    pandas.DataFrame
        A summary table with one row per neighbourhood group containing:
        - neighbourhood_group  : name of the area
        - mean_availability    : average days available per year (valid range only)
        - median_availability  : median days available per year
        - total_listings       : total number of listings in that group

    Raises
    ------
    KeyError
        If `neighbourhood_group` or `availability_365` columns are missing.

    Examples
    --------
    >>> from src.data_loader import load_data
    >>> df = load_data("data/Airbnb_NYC.csv")
    >>> result = compare_availability_by_neighbourhood(df)
    >>> print(result["neighbourhood_group"].tolist())
    ['Staten Island', 'Bronx', 'Queens', 'Brooklyn', 'Manhattan']
    """

    # Work on a copy so the caller's DataFrame is never modified
    df = df.copy()

    # ------------------------------------------------------------------
    # Step 1: Normalise neighbourhood_group — strip whitespace and title-case
    # e.g. 'brooklyn', 'BROOKLYN', '  Brooklyn  ' all become 'Brooklyn'
    # ------------------------------------------------------------------
    df["neighbourhood_group"] = df["neighbourhood_group"].str.strip().str.title()

    # ------------------------------------------------------------------
    # Step 2: Convert availability_365 to numeric
    # errors="coerce" safely converts bad values to NaN instead of crashing
    # ------------------------------------------------------------------
    df["availability_365"] = pd.to_numeric(df["availability_365"], errors="coerce")

    # ------------------------------------------------------------------
    # Step 3: Filter out invalid values outside [0, 365]
    # Values like 999 are data errors that would skew the statistics
    # ------------------------------------------------------------------
    df.loc[
        (df["availability_365"] < 0) |
        (df["availability_365"] > 365) |
        (df["availability_365"] % 1 != 0),
        "availability_365"
    ] = pd.NA
    
    
    # ------------------------------------------------------------------
    # Step 4: Group by neighbourhood and compute stats
    # - mean   : average valid availability across listings in the group
    # - median : middle value (less affected by extreme outliers)
    # - size   : total number of listings (including those with NaN
    #            availability), so the count reflects all listings in
    #            the group rather than only those with valid values
    # ------------------------------------------------------------------
    grouped = (
        df.groupby("neighbourhood_group")
        .agg(
            mean_availability=("availability_365", "mean"),
            median_availability=("availability_365", "median"),
            total_listings=("availability_365", "size"),
        )
        .round(2)
        # Sort highest availability first so the table is easy to read
        .sort_values("mean_availability", ascending=False)
        .reset_index()
    )

    # ------------------------------------------------------------------
    # Step 5: Print a clean summary table to the console
    # ------------------------------------------------------------------
    print("Availability by Neighbourhood Group")
    print("=" * 55)
    print(grouped.to_string(index=False))
    print("=" * 55)

    return grouped


# =============================================================================
# Script entry point
# -----------------------------------------------------------------------------
# Run this file directly to see the neighbourhood comparison:
#   python src/neighbourhood_availability.py
# =============================================================================

if __name__ == "__main__":
    from pathlib import Path
    from data_loader import load_data

    dataset_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "Airbnb_NYC.csv"
    )

    airbnb_df = load_data(dataset_path)
    compare_availability_by_neighbourhood(airbnb_df)