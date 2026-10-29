
"""
NYC Airbnb Neighbourhood Group Analysis.

CPSC620 - TASK-09 / Issue #13.

Summarize Airbnb listings by neighbourhood group.
"""

import pandas as pd


def summarize_listings_by_neighbourhood_group(df):
    """
    Count Airbnb listings by neighbourhood group.

    Includes listings regardless of their price and
    calculates each group's percentage of valid
    neighbourhood-group records.

    Parameters
    ----------
    df : pandas.DataFrame
        Original NYC Airbnb dataset.

    Returns
    -------
    pandas.DataFrame
        Columns:
        - neighbourhood_group
        - listing_count
        - percentage

        Sorted by listing_count descending.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    if "neighbourhood_group" not in df.columns:
        raise ValueError(
            "Missing required column: neighbourhood_group"
        )

    groups = (
        df["neighbourhood_group"]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

    # Exclude missing or blank group names.
    groups = groups.dropna()
    groups = groups.loc[groups.ne("")]

    # Normalize inconsistent capitalization.
    standard_names = {
        "bronx": "Bronx",
        "brooklyn": "Brooklyn",
        "manhattan": "Manhattan",
        "queens": "Queens",
        "staten island": "Staten Island"
    }

    groups = groups.map(
        lambda value: standard_names.get(
            value, value.title()
        )
    )

    result = (
        groups.value_counts()
        .rename_axis("neighbourhood_group")
        .reset_index(name="listing_count")
    )

    total = result["listing_count"].sum()

    if total:
        result["percentage"] = (
            result["listing_count"] / total * 100
        ).round(2)
    else:
        result["percentage"] = pd.Series(
            dtype="float64"
        )

    return result.reset_index(drop=True)
