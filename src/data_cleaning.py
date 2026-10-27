
"""
NYC Airbnb Data Cleaning
-----------------------
Course: CPSC620
Project: NYC Airbnb Data Summary Tool
Task: TASK-03 / Issue #5

Reusable cleaning functions for the NYC Airbnb dataset.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from src.data_loader import load_data


REQUIRED_COLUMNS = [
    "id",
    "neighbourhood_group",
    "neighbourhood",
    "room_type",
    "price",
    "minimum_nights",
    "availability_365",
]


def _validate_columns(df):
    """Validate input type and required columns."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    missing = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )


def clean_data(df):
    """
    Clean the NYC Airbnb dataset.

    Cleaning strategies
    -------------------
    1. Remove unnecessary whitespace from text columns.
    2. Replace missing listing and host names with placeholders.
    3. Remove rows missing essential listing information.
    4. Convert relevant fields to numeric values.
    5. Remove invalid prices, nights, and availability.
    6. Remove exact duplicates and repeated listing IDs.
    7. Preserve missing review dates when no date exists.

    Parameters
    ----------
    df : pandas.DataFrame
        Original Airbnb dataset.

    Returns
    -------
    pandas.DataFrame
        A cleaned, independent DataFrame.

    Raises
    ------
    TypeError
        If df is not a DataFrame.
    ValueError
        If required columns are missing.

    Notes
    -----
    Price must be positive and finite.
    Minimum nights must be a positive whole number.
    Availability must be a whole number from 0 to 365.
    For duplicate listing IDs, the first row is retained.
    The original DataFrame is never modified.
    """
    _validate_columns(df)

    cleaned = df.copy(deep=True)

    # 1. Normalize text fields.
    text_columns = [
        "name",
        "host_name",
        "neighbourhood_group",
        "neighbourhood",
        "room_type",
    ]

    for col in text_columns:
        if col in cleaned.columns:
            cleaned[col] = (
                cleaned[col]
                .astype("string")
                .str.strip()
                .replace("", pd.NA)
            )

    # 2. Handle optional missing names.
    if "name" in cleaned.columns:
        cleaned["name"] = (
            cleaned["name"].fillna("Unknown listing")
        )

    if "host_name" in cleaned.columns:
        cleaned["host_name"] = (
            cleaned["host_name"].fillna("Unknown host")
        )

    # 3. Remove rows missing essential information.
    essential_columns = [
        "id",
        "neighbourhood_group",
        "neighbourhood",
        "room_type",
    ]

    cleaned = cleaned.dropna(
        subset=essential_columns
    ).copy()

    # 4. Convert numeric columns.
    numeric_columns = [
        "price",
        "minimum_nights",
        "availability_365",
    ]

    for col in numeric_columns:
        cleaned[col] = (
            pd.to_numeric(cleaned[col], errors="coerce")
            .replace([np.inf, -np.inf], np.nan)
        )

    # 5. Identify valid numerical values.
    valid_price = cleaned["price"] > 0

    valid_nights = (
        (cleaned["minimum_nights"] >= 1)
        & (cleaned["minimum_nights"] % 1 == 0)
    )

    valid_availability = (
        cleaned["availability_365"].between(0, 365)
        & (cleaned["availability_365"] % 1 == 0)
    )

    valid_rows = (
        valid_price
        & valid_nights
        & valid_availability
    )

    cleaned = cleaned.loc[valid_rows].copy()

    # 6. Handle optional review fields.
    for col in ["number_of_reviews", "reviews_per_month"]:
        if col in cleaned.columns:
            cleaned[col] = pd.to_numeric(
                cleaned[col], errors="coerce"
            )

            cleaned.loc[
                cleaned[col] < 0, col
            ] = np.nan

    # A listing with zero reviews has a review rate of zero.
    if (
        "number_of_reviews" in cleaned.columns
        and "reviews_per_month" in cleaned.columns
    ):
        zero_reviews = (
            cleaned["number_of_reviews"] == 0
        )

        cleaned.loc[
            zero_reviews
            & cleaned["reviews_per_month"].isna(),
            "reviews_per_month",
        ] = 0.0

    # Missing last_review dates are preserved.
    # They may legitimately represent listings without reviews.

    # 7. Remove duplicate records.
    cleaned = cleaned.drop_duplicates(
        keep="first"
    )

    # Listing IDs should identify unique properties.
    cleaned = cleaned.drop_duplicates(
        subset=["id"],
        keep="first"
    )

    return cleaned.reset_index(drop=True)


if __name__ == "__main__":
    dataset_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "Airbnb_NYC.csv"
    )

    original_df = load_data(dataset_path)
    cleaned_df = clean_data(original_df)

    print("\nNYC AIRBNB DATA CLEANING REPORT")
    print("=" * 45)

    print(f"Original rows: {len(original_df)}")
    print(f"Cleaned rows: {len(cleaned_df)}")
    print(
        "Removed rows: "
        f"{len(original_df) - len(cleaned_df)}"
    )

    print("\nRemaining duplicate IDs:")
    print(cleaned_df["id"].duplicated().sum())

    print("\nRemaining invalid prices:")
    print((cleaned_df["price"] <= 0).sum())

    print("\nFirst five cleaned records:")
    print(cleaned_df.head().to_string(index=False))

    print("\nData cleaning completed successfully.")
