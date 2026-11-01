import numpy as np
import pandas as pd
import pytest

from src.review_analysis import analyze_overall_reviews
from src.review_comparison import (
    compare_reviews_by_room_type,
    compare_reviews_by_neighbourhood,
)


@pytest.fixture
def sample_reviews():
    """Create a small dataset for review integration testing."""
    return pd.DataFrame(
        {
            "room_type": [
                "Private room",
                "Entire home/apt",
                "Private room",
                "Shared room",
                "Entire home/apt",
            ],
            "neighbourhood_group": [
                "Brooklyn",
                "Manhattan",
                "Brooklyn",
                "Queens",
                "Manhattan",
            ],
            "number_of_reviews": [10, 20, 0, 30, 40],
            "reviews_per_month": [1.0, 2.0, 0.0, 3.0, 4.0],
        }
    )


@pytest.fixture
def invalid_reviews():
    """Create a dataset containing valid and invalid review values."""
    return pd.DataFrame(
        {
            "room_type": [
                "Private room",
                "Private room",
                "Shared room",
                "Shared room",
                "Entire home/apt",
            ],
            "neighbourhood_group": [
                "Brooklyn",
                "Brooklyn",
                "Queens",
                "Queens",
                "Manhattan",
            ],
            "number_of_reviews": [10, -5, 20, None, 30],
            "reviews_per_month": [1.0, -2.0, 2.0, None, 3.0],
        }
    )


def test_overall_review_statistics(sample_reviews):
    """Verify overall totals, averages, and zero-review listings."""
    result = analyze_overall_reviews(sample_reviews)

    assert result["total_listings"] == 5
    assert result["total_reviews"] == 100
    assert result["average_reviews_per_listing"] == pytest.approx(20.0)
    assert result["zero_review_listings"] == 1
    assert result["average_reviews_per_month"] == pytest.approx(2.0)


def test_room_type_review_summary(sample_reviews):
    """Verify review statistics grouped by room type."""
    result = compare_reviews_by_room_type(sample_reviews)

    assert result["listing_count"].sum() == 5

    private_room = result.loc[
        result["room_type"].str.strip().str.casefold() == "private room"
    ].iloc[0]

    assert private_room["listing_count"] == 2
    assert private_room["average_reviews"] == pytest.approx(5.0)
    assert private_room["average_reviews_per_month"] == pytest.approx(0.5)


def test_neighbourhood_review_summary(sample_reviews):
    """Verify review statistics grouped by neighbourhood."""
    result = compare_reviews_by_neighbourhood(sample_reviews)

    assert result["listing_count"].sum() == 5

    brooklyn = result.loc[
        result["neighbourhood_group"].str.strip().str.casefold() == "brooklyn"
    ].iloc[0]

    assert brooklyn["listing_count"] == 2
    assert brooklyn["average_reviews"] == pytest.approx(5.0)
    assert brooklyn["average_reviews_per_month"] == pytest.approx(0.5)


def test_review_totals_are_consistent_across_modules(sample_reviews):
    """Check consistency across modules when all review values are valid."""
    overall = analyze_overall_reviews(sample_reviews)
    by_room = compare_reviews_by_room_type(sample_reviews)
    by_neighbourhood = compare_reviews_by_neighbourhood(sample_reviews)

    room_total = (
        by_room["average_reviews"] * by_room["listing_count"]
    ).sum()

    neighbourhood_total = (
        by_neighbourhood["average_reviews"]
        * by_neighbourhood["listing_count"]
    ).sum()

    assert room_total == pytest.approx(overall["total_reviews"])
    assert neighbourhood_total == pytest.approx(overall["total_reviews"])


def test_invalid_review_values_across_modules():
    """Verify that invalid values are excluded from grouped averages."""
    df = pd.DataFrame(
        {
            "room_type": [
                "Private room",
                "Private room",
                "Shared room",
            ],
            "neighbourhood_group": [
                "Brooklyn",
                "Brooklyn",
                "Queens",
            ],
            "number_of_reviews": [10, -5, None],
            "reviews_per_month": [1.0, -2.0, None],
        }
    )

    overall = analyze_overall_reviews(df)
    by_room = compare_reviews_by_room_type(df)
    by_neighbourhood = compare_reviews_by_neighbourhood(df)

    assert overall["total_reviews"] == 10
    assert overall["invalid_review_counts"] == 2
    assert overall["invalid_monthly_reviews"] == 2
    assert overall["valid_review_listing_count"] == 1

    assert by_room["listing_count"].sum() == 3
    assert by_neighbourhood["listing_count"].sum() == 3

    private_room = by_room.loc[
        by_room["room_type"] == "private room"
    ].iloc[0]

    brooklyn = by_neighbourhood.loc[
        by_neighbourhood["neighbourhood_group"] == "Brooklyn"
    ].iloc[0]

    # Invalid review counts must not affect grouped averages.
    assert private_room["average_reviews"] == pytest.approx(10.0)
    assert brooklyn["average_reviews"] == pytest.approx(10.0)

    # Invalid monthly review values must also be excluded.
    assert private_room["average_reviews_per_month"] == pytest.approx(1.0)
    assert brooklyn["average_reviews_per_month"] == pytest.approx(1.0)

    # Listing counts still include records with invalid review values.
    assert private_room["listing_count"] == 2
    assert brooklyn["listing_count"] == 2

    # Groups without valid review counts must have NaN averages.
    shared_room = by_room.loc[
        by_room["room_type"] == "shared room"
    ].iloc[0]

    assert np.isnan(shared_room["average_reviews"])
    assert np.isnan(shared_room["average_reviews_per_month"])


def test_review_totals_with_invalid_data_are_consistent(invalid_reviews):
    """
    Verify cross-module consistency when invalid review values exist.

    Grouped averages are calculated using valid review counts only.
    Listing counts include all records, so they cannot be used
    directly to reconstruct review totals when invalid data exists.
    """
    overall = analyze_overall_reviews(invalid_reviews)
    by_room = compare_reviews_by_room_type(invalid_reviews)
    by_neighbourhood = compare_reviews_by_neighbourhood(invalid_reviews)

    # Expected total from valid review counts: 10 + 20 + 30.
    assert overall["total_reviews"] == 60
    assert overall["valid_review_listing_count"] == 3
    assert overall["invalid_review_counts"] == 2

    # All five listings remain represented in grouped summaries.
    assert by_room["listing_count"].sum() == 5
    assert by_neighbourhood["listing_count"].sum() == 5

    # Expected averages after excluding invalid review values.
    expected_room_averages = {
        "private room": 10.0,
        "shared room": 20.0,
        "entire home/apt": 30.0,
    }

    expected_neighbourhood_averages = {
        "Brooklyn": 10.0,
        "Queens": 20.0,
        "Manhattan": 30.0,
    }

    for room_type, expected_average in expected_room_averages.items():
        row = by_room.loc[
            by_room["room_type"] == room_type
        ].iloc[0]

        assert row["average_reviews"] == pytest.approx(expected_average)

    for neighbourhood, expected_average in expected_neighbourhood_averages.items():
        row = by_neighbourhood.loc[
            by_neighbourhood["neighbourhood_group"] == neighbourhood
        ].iloc[0]

        assert row["average_reviews"] == pytest.approx(expected_average)

    # Each group contains exactly one valid review count.
    valid_counts_by_room = {
        "private room": 1,
        "shared room": 1,
        "entire home/apt": 1,
    }

    valid_counts_by_neighbourhood = {
        "Brooklyn": 1,
        "Queens": 1,
        "Manhattan": 1,
    }

    room_total = sum(
        row["average_reviews"]
        * valid_counts_by_room[row["room_type"]]
        for _, row in by_room.iterrows()
    )

    neighbourhood_total = sum(
        row["average_reviews"]
        * valid_counts_by_neighbourhood[row["neighbourhood_group"]]
        for _, row in by_neighbourhood.iterrows()
    )

    assert room_total == pytest.approx(overall["total_reviews"])
    assert neighbourhood_total == pytest.approx(overall["total_reviews"])


def test_integration_does_not_modify_original_data(sample_reviews):
    """Ensure that running all analyses preserves the input DataFrame."""
    original = sample_reviews.copy(deep=True)

    analyze_overall_reviews(sample_reviews)
    compare_reviews_by_room_type(sample_reviews)
    compare_reviews_by_neighbourhood(sample_reviews)

    pd.testing.assert_frame_equal(sample_reviews, original)


def test_empty_dataset_across_modules():
    """Verify that all modules handle an empty dataset."""
    df = pd.DataFrame(
        columns=[
            "room_type",
            "neighbourhood_group",
            "number_of_reviews",
            "reviews_per_month",
        ]
    )

    overall = analyze_overall_reviews(df)
    by_room = compare_reviews_by_room_type(df)
    by_neighbourhood = compare_reviews_by_neighbourhood(df)

    assert overall["total_listings"] == 0
    assert overall["total_reviews"] == 0
    assert by_room.empty
    assert by_neighbourhood.empty