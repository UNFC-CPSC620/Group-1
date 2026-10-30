# =============================================================================
# review_analysis.py
# -----------------------------------------------------------------------------
# TASK-15: Analyze Overall Airbnb Reviews
#
# Calculates overall review statistics for NYC Airbnb listings.
# =============================================================================

import numpy as np
import pandas as pd


def analyze_overall_reviews(df):
    """
    Calculate overall review statistics for NYC Airbnb listings.

    The function analyzes the number of reviews and average monthly
    review activity for each listing.

    Missing, negative, non-numeric, infinite, and invalid review counts
    are excluded from calculations. The original DataFrame is not modified.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataset containing:
        - number_of_reviews
        - reviews_per_month

    Returns
    -------
    dict
        Dictionary containing:
        - total_listings
        - total_reviews
        - valid_review_listing_count
        - average_reviews_per_listing
        - zero_review_listings
        - average_reviews_per_month
        - invalid_review_counts
        - invalid_monthly_reviews

    Raises
    ------
    TypeError
        If the input is not a pandas DataFrame.
    KeyError
        If required columns are missing.
    """

    # Validate input type.
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    # Validate required columns.
    required_columns = ["number_of_reviews", "reviews_per_month"]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise KeyError(f"Missing required columns: {missing_columns}")

    # Convert values to numeric without modifying the original DataFrame.
    review_counts = pd.to_numeric(
        df["number_of_reviews"], errors="coerce"
    )

    monthly_reviews = pd.to_numeric(
        df["reviews_per_month"], errors="coerce"
    )

    # Valid total review counts must be finite, non-negative integers.
    valid_review_counts = (
        np.isfinite(review_counts)
        & (review_counts >= 0)
        & (review_counts % 1 == 0)
    ).fillna(False)

    # Valid monthly review activity must be finite and non-negative.
    valid_monthly_reviews = (
        np.isfinite(monthly_reviews)
        & (monthly_reviews >= 0)
    ).fillna(False)

    # Keep only valid values for calculations.
    valid_counts = review_counts[valid_review_counts]
    valid_monthly = monthly_reviews[valid_monthly_reviews]

    # Calculate listing and review statistics.
    total_listings = len(df)
    valid_review_listing_count = int(valid_review_counts.sum())
    total_reviews = int(valid_counts.sum())

    # Calculate average reviews using only listings with valid review counts.
    average_reviews = (
        total_reviews / valid_review_listing_count
        if valid_review_listing_count > 0 else 0.0
    )

    # Count listings with zero reviews among valid review counts.
    zero_review_listings = int((valid_counts == 0).sum())

    # Calculate average monthly review activity.
    average_monthly_reviews = (
        valid_monthly.mean()
        if not valid_monthly.empty else 0.0
    )

    # Return reusable structured results.
    return {
        "total_listings": total_listings,
        "total_reviews": total_reviews,
        "valid_review_listing_count": valid_review_listing_count,
        "average_reviews_per_listing": round(average_reviews, 2),
        "zero_review_listings": zero_review_listings,
        "average_reviews_per_month": round(
            float(average_monthly_reviews), 2
        ),
        "invalid_review_counts": int((~valid_review_counts).sum()),
        "invalid_monthly_reviews": int(
            (~valid_monthly_reviews).sum()
        ),
    }
