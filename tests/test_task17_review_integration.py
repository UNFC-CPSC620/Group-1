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
    """Check that overall and grouped review results are consistent."""
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
    """Check that invalid review values do not break the analysis."""
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

    assert by_room["listing_count"].sum() == 3
    assert by_neighbourhood["listing_count"].sum() == 3


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