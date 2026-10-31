import pandas as pd
import numpy as np


def compare_reviews_by_room_type(df):
    """
    Compare Airbnb review activity across room types.

    Calculates the average total reviews and average monthly
    reviews for each room type.

    Parameters
    ----------
    df : pandas.DataFrame
        Airbnb dataset containing room_type, number_of_reviews,
        and reviews_per_month.

    Returns
    -------
    pandas.DataFrame
        Review statistics grouped by room type.
    """
    required_columns = [
        "room_type",
        "number_of_reviews",
        "reviews_per_month"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    data = df[required_columns].copy()

    data["number_of_reviews"] = pd.to_numeric(
        data["number_of_reviews"], errors="coerce"
    )

    data["reviews_per_month"] = pd.to_numeric(
        data["reviews_per_month"], errors="coerce"
    )

    # Keep only finite, non-negative whole-number review counts.
    valid_review_counts = (
        np.isfinite(data["number_of_reviews"])
        & (data["number_of_reviews"] >= 0)
        & (data["number_of_reviews"] % 1 == 0)
    ).fillna(False)

    data["number_of_reviews"] = data["number_of_reviews"].where(
        valid_review_counts
    )

    # Monthly review activity can contain valid decimal values.
    valid_monthly_reviews = (
        np.isfinite(data["reviews_per_month"])
        & (data["reviews_per_month"] >= 0)
    ).fillna(False)

    data["reviews_per_month"] = data["reviews_per_month"].where(
        valid_monthly_reviews
    )

    data["room_type"] = (
        data["room_type"].astype("string").str.strip().str.lower()
    )

    data = data.dropna(subset=["room_type"])
    data = data[data["room_type"] != ""]

    summary = (
        data.groupby("room_type")
        .agg(
            average_reviews=("number_of_reviews", "mean"),
            average_reviews_per_month=("reviews_per_month", "mean"),
            listing_count=("room_type", "size")
        )
        .reset_index()
        .sort_values("room_type")
        .reset_index(drop=True)
    )

    return summary


def compare_reviews_by_neighbourhood(df):
    """
    Compare Airbnb review activity across neighbourhood groups.

    Calculates average total reviews and average monthly reviews
    for each neighbourhood group.

    Parameters
    ----------
    df : pandas.DataFrame
        Airbnb dataset containing neighbourhood_group,
        number_of_reviews, and reviews_per_month.

    Returns
    -------
    pandas.DataFrame
        Review statistics grouped by neighbourhood group.
    """
    required_columns = [
        "neighbourhood_group",
        "number_of_reviews",
        "reviews_per_month"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    data = df[required_columns].copy()

    data["number_of_reviews"] = pd.to_numeric(
        data["number_of_reviews"], errors="coerce"
    )

    data["reviews_per_month"] = pd.to_numeric(
        data["reviews_per_month"], errors="coerce"
    )

    # Keep only finite, non-negative whole-number review counts.
    valid_review_counts = (
        np.isfinite(data["number_of_reviews"])
        & (data["number_of_reviews"] >= 0)
        & (data["number_of_reviews"] % 1 == 0)
    ).fillna(False)

    data["number_of_reviews"] = data["number_of_reviews"].where(
        valid_review_counts
    )

    # Monthly review activity can contain valid decimal values.
    valid_monthly_reviews = (
        np.isfinite(data["reviews_per_month"])
        & (data["reviews_per_month"] >= 0)
    ).fillna(False)

    data["reviews_per_month"] = data["reviews_per_month"].where(
        valid_monthly_reviews
    )

    data["neighbourhood_group"] = (
        data["neighbourhood_group"]
        .astype("string")
        .str.strip()
        .str.title()
    )

    data = data.dropna(subset=["neighbourhood_group"])
    data = data[data["neighbourhood_group"] != ""]

    summary = (
        data.groupby("neighbourhood_group")
        .agg(
            average_reviews=("number_of_reviews", "mean"),
            average_reviews_per_month=("reviews_per_month", "mean"),
            listing_count=("neighbourhood_group", "size")
        )
        .reset_index()
        .sort_values("neighbourhood_group")
        .reset_index(drop=True)
    )

    return summary
