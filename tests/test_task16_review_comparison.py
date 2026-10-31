import pandas as pd
import pytest

from src.review_comparison import (
    compare_reviews_by_room_type,
    compare_reviews_by_neighbourhood
)


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "room_type": [
            "Private room",
            "PRIVATE ROOM",
            "Entire home/apt",
            "Shared room",
            "private room",
            "Entire home/apt"
        ],
        "neighbourhood_group": [
            "Brooklyn",
            "Manhattan",
            "Queens",
            "Bronx",
            "Brooklyn",
            "Queens"
        ],
        "number_of_reviews": [
            10, 20, 30, 40, 0, 50
        ],
        "reviews_per_month": [
            1.0, 2.0, 3.0, 4.0, 0.0, 5.0
        ]
    })


def test_compare_reviews_by_room_type(sample_data):
    result = compare_reviews_by_room_type(sample_data)

    assert len(result) == 3
    assert set(result["room_type"]) == {
        "private room",
        "entire home/apt",
        "shared room"
    }

    private_room = result[
        result["room_type"] == "private room"
    ].iloc[0]

    assert private_room["average_reviews"] == 10
    assert private_room["average_reviews_per_month"] == 1
    assert private_room["listing_count"] == 3


def test_compare_reviews_by_neighbourhood(sample_data):
    result = compare_reviews_by_neighbourhood(sample_data)

    assert len(result) == 4

    brooklyn = result[
        result["neighbourhood_group"] == "Brooklyn"
    ].iloc[0]

    assert brooklyn["average_reviews"] == 5
    assert brooklyn["average_reviews_per_month"] == 0.5
    assert brooklyn["listing_count"] == 2


def test_missing_values_are_handled():
    df = pd.DataFrame({
        "room_type": ["Private room", "Private room", None],
        "neighbourhood_group": ["Brooklyn", "Brooklyn", "Queens"],
        "number_of_reviews": [10, None, 20],
        "reviews_per_month": [1.0, 2.0, None]
    })

    result = compare_reviews_by_room_type(df)

    private_room = result.iloc[0]

    assert private_room["average_reviews"] == 10
    assert private_room["average_reviews_per_month"] == 1.5
    assert private_room["listing_count"] == 2


def test_invalid_values_are_ignored():
    df = pd.DataFrame({
        "room_type": ["Private room"] * 4,
        "neighbourhood_group": ["Brooklyn"] * 4,
        "number_of_reviews": [10, -5, "invalid", 20],
        "reviews_per_month": [1.0, -2.0, "invalid", 3.0]
    })

    result = compare_reviews_by_room_type(df)

    assert result.iloc[0]["average_reviews"] == 15
    assert result.iloc[0]["average_reviews_per_month"] == 2


def test_fractional_review_counts_are_excluded_by_room_type():
    df = pd.DataFrame({
        "room_type": ["Private room"] * 3,
        "number_of_reviews": [10, 2.5, 20],
        "reviews_per_month": [1.0, 2.0, 3.0]
    })

    result = compare_reviews_by_room_type(df)

    assert result.iloc[0]["average_reviews"] == 15
    assert result.iloc[0]["average_reviews_per_month"] == 2
    assert result.iloc[0]["listing_count"] == 3


def test_fractional_review_counts_are_excluded_by_neighbourhood():
    df = pd.DataFrame({
        "neighbourhood_group": ["Brooklyn"] * 3,
        "number_of_reviews": [10, 2.5, 20],
        "reviews_per_month": [1.0, 2.0, 3.0]
    })

    result = compare_reviews_by_neighbourhood(df)

    assert result.iloc[0]["average_reviews"] == 15
    assert result.iloc[0]["average_reviews_per_month"] == 2
    assert result.iloc[0]["listing_count"] == 3


def test_nullable_pandas_columns_are_handled():
    df = pd.DataFrame({
        "room_type": ["Private room"] * 3,
        "neighbourhood_group": ["Brooklyn"] * 3,
        "number_of_reviews": pd.Series(
            [10, pd.NA, 20], dtype="Int64"
        ),
        "reviews_per_month": pd.Series(
            [1.5, pd.NA, 2.5], dtype="Float64"
        )
    })

    room_result = compare_reviews_by_room_type(df)
    neighbourhood_result = compare_reviews_by_neighbourhood(df)

    assert room_result.iloc[0]["average_reviews"] == 15
    assert room_result.iloc[0]["average_reviews_per_month"] == 2
    assert room_result.iloc[0]["listing_count"] == 3

    assert neighbourhood_result.iloc[0]["average_reviews"] == 15
    assert neighbourhood_result.iloc[0]["average_reviews_per_month"] == 2
    assert neighbourhood_result.iloc[0]["listing_count"] == 3


def test_original_dataframe_is_not_modified(sample_data):
    original = sample_data.copy(deep=True)

    compare_reviews_by_room_type(sample_data)
    compare_reviews_by_neighbourhood(sample_data)

    pd.testing.assert_frame_equal(sample_data, original)


def test_missing_required_columns_raise_error():
    df = pd.DataFrame({
        "room_type": ["Private room"],
        "number_of_reviews": [10]
    })

    with pytest.raises(ValueError, match="Missing required columns"):
        compare_reviews_by_room_type(df)

    with pytest.raises(ValueError, match="Missing required columns"):
        compare_reviews_by_neighbourhood(df)
