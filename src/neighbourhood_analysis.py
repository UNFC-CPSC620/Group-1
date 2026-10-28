
"""
NYC Airbnb Neighbourhood Analysis
--------------------------------
Course: CPSC620
Project: NYC Airbnb Data Summary Tool
Task: TASK-10 / Issue #14

Reusable Pandas functions for analysing listing prices
and neighbourhood listing counts.
"""

import pandas as pd


def clean_price_data(df):
    """
    Validate Airbnb data and exclude invalid prices.

    Parameters
    ----------
    df : pandas.DataFrame
        Airbnb listings dataset.

    Returns
    -------
    pandas.DataFrame
        Copy containing only valid, positive, finite prices.

    Raises
    ------
    TypeError
        If the input is not a DataFrame.
    ValueError
        If the price column is missing.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    if "price" not in df.columns:
        raise ValueError("Missing required column: price")

    cleaned = df.copy()

    cleaned["price"] = pd.to_numeric(
        cleaned["price"],
        errors="coerce"
    )

    valid = (
        cleaned["price"].notna()
        & (cleaned["price"] > 0)
        & (cleaned["price"] < float("inf"))
    )

    return cleaned.loc[valid].copy()


def _prepare_neighbourhood_data(df, columns):
    """
    Prepare and validate neighbourhood data.

    Removes missing or empty neighbourhood labels.
    Standardizes NYC neighbourhood group names.
    Normalizes neighbourhood names regardless of case,
    preserving the most frequent spelling.

    Parameters
    ----------
    df : pandas.DataFrame
        Original Airbnb dataset.
    columns : list
        Required grouping columns.

    Returns
    -------
    pandas.DataFrame
        Cleaned dataset with standardized group and
        neighbourhood names.
    """
    cleaned = clean_price_data(df)

    missing = [
        column
        for column in columns
        if column not in cleaned.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    # Remove missing or empty grouping values.
    for column in columns:
        cleaned[column] = (
            cleaned[column]
            .astype("string")
            .str.strip()
        )

        valid_group = (
            cleaned[column].notna()
            & cleaned[column].ne("")
        )

        cleaned = cleaned.loc[valid_group].copy()

    # Standardize NYC neighbourhood group names.
    if "neighbourhood_group" in columns:

        standard_names = {
            "bronx": "Bronx",
            "brooklyn": "Brooklyn",
            "manhattan": "Manhattan",
            "queens": "Queens",
            "staten island": "Staten Island"
        }

        standardized = (
            cleaned["neighbourhood_group"]
            .str.casefold()
            .map(standard_names)
        )

        cleaned["neighbourhood_group"] = (
            standardized.fillna(
                cleaned["neighbourhood_group"]
            )
        )

    # Normalize neighbourhood names (case insensitive).
    # Keep the most frequently used spelling.
    # For example: "Tribeca" and "tribeca" become "Tribeca".
    if "neighbourhood" in columns:

        name_counts = (
            cleaned["neighbourhood"]
            .value_counts()
        )

        canonical_names = {}

        for name in name_counts.index:
            normalized_name = name.casefold()

            if normalized_name not in canonical_names:
                canonical_names[normalized_name] = name

        cleaned["neighbourhood"] = (
            cleaned["neighbourhood"]
            .str.casefold()
            .map(canonical_names)
        )

    return cleaned


def average_prices_by_group(df):
    """
    Calculate average listing prices by neighbourhood group.

    Parameters
    ----------
    df : pandas.DataFrame
        Airbnb listings dataset.

    Returns
    -------
    pandas.DataFrame
        Columns:
        - neighbourhood_group
        - average_price
        - listing_count

        Results sorted by average price descending.
        Counts include only valid-price listings.
    """
    cleaned = _prepare_neighbourhood_data(
        df,
        ["neighbourhood_group"]
    )

    result = cleaned.groupby(
        "neighbourhood_group",
        as_index=False
    ).agg(
        average_price=("price", "mean"),
        listing_count=("price", "size")
    )

    result["average_price"] = (
        result["average_price"].round(2)
    )

    return (
        result.sort_values(
            "average_price",
            ascending=False
        )
        .reset_index(drop=True)
    )


def average_prices_by_neighbourhood(df):
    """
    Calculate average prices for individual neighbourhoods.

    Neighbourhood names are normalized so that spelling
    differences in capitalization do not create
    duplicate neighbourhood groups.

    Parameters
    ----------
    df : pandas.DataFrame
        Airbnb listings dataset.

    Returns
    -------
    pandas.DataFrame
        Columns:
        - neighbourhood_group
        - neighbourhood
        - average_price
        - listing_count

        Results sorted by average price descending.
        Counts include only valid-price listings.
    """
    columns = [
        "neighbourhood_group",
        "neighbourhood"
    ]

    cleaned = _prepare_neighbourhood_data(
        df,
        columns
    )

    result = cleaned.groupby(
        columns,
        as_index=False
    ).agg(
        average_price=("price", "mean"),
        listing_count=("price", "size")
    )

    result["average_price"] = (
        result["average_price"].round(2)
    )

    return (
        result.sort_values(
            "average_price",
            ascending=False
        )
        .reset_index(drop=True)
    )


def top_neighbourhoods_by_listings(df, top_n=10):
    """
    Identify neighbourhoods with the most valid-price listings.

    Neighbourhood names are normalized before counting
    so capitalization differences do not split listings.

    Parameters
    ----------
    df : pandas.DataFrame
        Airbnb listings dataset.
    top_n : int, default=10
        Number of neighbourhoods to return.

    Returns
    -------
    pandas.DataFrame
        Columns:
        - neighbourhood_group
        - neighbourhood
        - listing_count

        Results sorted by listing count descending.

    Raises
    ------
    ValueError
        If top_n is not a positive integer.
    """
    if (
        isinstance(top_n, bool)
        or not isinstance(top_n, int)
        or top_n < 1
    ):
        raise ValueError(
            "top_n must be a positive integer."
        )

    columns = [
        "neighbourhood_group",
        "neighbourhood"
    ]

    cleaned = _prepare_neighbourhood_data(
        df,
        columns
    )

    result = cleaned.groupby(
        columns,
        as_index=False
    ).agg(
        listing_count=("price", "size")
    )

    result = result.sort_values(
        by=[
            "listing_count",
            "neighbourhood_group",
            "neighbourhood"
        ],
        ascending=[False, True, True]
    )

    return (
        result.head(top_n)
        .reset_index(drop=True)
    )
