# =============================================================================
# availability_analysis.py
# -----------------------------------------------------------------------------
# TASK-12: Analyze Overall Airbnb Availability
#
# This module analyzes the `availability_365` column from the NYC Airbnb
# dataset. It computes summary statistics to understand how available
# listings are throughout the year across all neighbourhoods.
#
# Author   : Alejandro (Kvothep)
# Issue    : #17
# Sprint   : Sprint 1
# =============================================================================

import pandas as pd


def analyze_overall_availability(df):
    """
    Analyze overall Airbnb availability across all listings.

    This function takes the full Airbnb DataFrame and computes descriptive
    statistics for the `availability_365` column — the number of days per
    year a listing is available for booking.

    Only values in the valid range [0, 365] are included in the
    calculations. The original DataFrame is never modified.

    Key metrics computed
    --------------------
    - Mean and median availability (central tendency)
    - Min and max (range)
    - Standard deviation (spread across listings)
    - Count of fully available listings (365 days)
    - Count of listings with zero availability

    Parameters
    ----------
    df : pandas.DataFrame
        The NYC Airbnb dataset. Must contain an `availability_365` column
        with integer values between 0 and 365.

    Returns
    -------
    dict
        A dictionary of summary statistics with the following keys:
        - total_listings       : total number of rows in the dataset
        - mean_availability    : average days available per year
        - median_availability  : middle value (less sensitive to outliers)
        - min_availability     : lowest availability found
        - max_availability     : highest availability found
        - std_availability     : standard deviation
        - fully_available      : count of listings available all 365 days
        - not_available        : count of listings with 0 available days

    Raises
    ------
    ValueError
        If the `availability_365` column is missing, or if no valid values
        remain after filtering out out-of-range and non-numeric entries.

    Examples
    --------
    >>> from src.data_loader import load_data
    >>> df = load_data("data/Airbnb_NYC.csv")
    >>> summary = analyze_overall_availability(df)
    >>> print(summary["mean_availability"])
    112.78
    """

    if "availability_365" not in df.columns:
        raise ValueError("The dataset must contain an 'availability_365' column.")

    # Work on a copy so the caller's DataFrame is never modified
    data = df.copy()

    # Convert to numeric — errors="coerce" turns non-numeric values into NaN
    data["availability_365"] = pd.to_numeric(
        data["availability_365"], errors="coerce"
    )

    # Filter to valid range [0, 365] only — removes NaN and out-of-range values
    # such as 999, which indicate data quality issues
    availability = data["availability_365"][
        (data["availability_365"] >= 0) & (data["availability_365"] <= 365)
    ]

    if availability.empty:
        raise ValueError(
            "No valid availability_365 values found in the dataset."
        )

    # ------------------------------------------------------------------
    # Build the summary dictionary
    # Each value is rounded or cast to keep output clean and readable
    # ------------------------------------------------------------------
    summary = {
        # total_listings counts all rows in the original dataset
        "total_listings"     : len(df),
        "mean_availability"  : round(float(availability.mean()), 2),
        "median_availability": round(float(availability.median()), 2),
        "min_availability"   : int(availability.min()),
        "max_availability"   : int(availability.max()),
        "std_availability"   : round(float(availability.std()), 2),
        # Count listings that are open every single day of the year
        "fully_available"    : int((availability == 365).sum()),
        # Count listings that are never available (blocked or inactive)
        "not_available"      : int((availability == 0).sum()),
    }

    # ------------------------------------------------------------------
    # Print a human-readable report to the console
    # ------------------------------------------------------------------
    print("Overall Airbnb Availability Analysis")
    print("=" * 45)
    print(f"  Total listings         : {summary['total_listings']:,}")
    print(f"  Mean availability      : {summary['mean_availability']} days/year")
    print(f"  Median availability    : {summary['median_availability']} days/year")
    print(f"  Min availability       : {summary['min_availability']} days")
    print(f"  Max availability       : {summary['max_availability']} days")
    print(f"  Std deviation          : {summary['std_availability']}")
    print("-" * 45)
    print(f"  Fully available (365d) : {summary['fully_available']:,} listings")
    print(f"  Not available   (0d)   : {summary['not_available']:,} listings")
    print("=" * 45)

    return summary


# =============================================================================
# Script entry point
# -----------------------------------------------------------------------------
# Run this file directly to see the analysis output:
#   python src/availability_analysis.py
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

    # Load the dataset and run the analysis
    airbnb_df = load_data(dataset_path)
    analyze_overall_availability(airbnb_df)
