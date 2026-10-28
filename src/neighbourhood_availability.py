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
    descriptive statistics for `availability_365` in each group. The result
    helps identify which areas of NYC have more or fewer available listings
    throughout the year.

    How it works
    ------------
    1. Converts `availability_365` to numeric (handles any string values)
    2. Groups the data by `neighbourhood_group`
    3. Computes mean, median, and listing count per group
    4. Sorts results from highest to lowest average availability
    5. Prints a formatted summary table to the console

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
        - mean_availability    : average days available per year
        - median_availability  : median days available per year
        - total_listings       : number of listings in that group

    Examples
    --------
    >>> from src.data_loader import load_data
    >>> df = load_data("data/Airbnb_NYC.csv")
    >>> result = compare_availability_by_neighbourhood(df)
    >>> print(result["neighbourhood_group"].tolist())
    ['Staten Island', 'Bronx', 'Queens', 'Brooklyn', 'Manhattan']
    """

    # ------------------------------------------------------------------
    # Step 1: Ensure availability_365 is numeric
    # Needed because pandas may read CSV columns as strings
    # errors="coerce" safely converts bad values to NaN instead of crashing
    # ------------------------------------------------------------------
    df["availability_365"] = pd.to_numeric(
        df["availability_365"], errors="coerce"
    )
   
   # Normalize neighbourhood_group casing to avoid duplicate groups
    # e.g. 'brooklyn', 'BROOKLYN', 'Brooklyn' all become 'Brooklyn'
    df["neighbourhood_group"] = df["neighbourhood_group"].str.strip().str.title()

    # ------------------------------------------------------------------
    # Step 2: Group by neighbourhood and compute stats
    # - mean   : average availability across all listings in the group
    # - median : middle value (less affected by extreme outliers)
    # - count  : total number of listings in that neighbourhood group
    # ------------------------------------------------------------------
    grouped = (
        df.groupby("neighbourhood_group")["availability_365"]
        .agg(
            mean_availability="mean",
            median_availability="median",
            total_listings="count",
        )
        .round(2)
        # Sort highest availability first so the table is easy to read
        .sort_values("mean_availability", ascending=False)
        .reset_index()
    )

    # ------------------------------------------------------------------
    # Step 3: Print a clean summary table to the console
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

    # Build path to the dataset relative to this file's location
    dataset_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "Airbnb_NYC.csv"
    )

    # Load the dataset and run the neighbourhood comparison
    airbnb_df = load_data(dataset_path)
    compare_availability_by_neighbourhood(airbnb_df)