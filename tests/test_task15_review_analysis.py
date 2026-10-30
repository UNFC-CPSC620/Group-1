import numpy as np
import pandas as pd
import pytest

from src.review_analysis import analyze_overall_reviews


class TestAnalyzeOverallReviews:

    def test_calculates_overall_review_statistics(self):
        df = pd.DataFrame({
            "number_of_reviews": [10, 20, 0, 30],
            "reviews_per_month": [2.0, 4.0, 0.0, 6.0]
        })

        result = analyze_overall_reviews(df)

        assert result["total_listings"] == 4
        assert result["total_reviews"] == 60
        assert result["average_reviews_per_listing"] == 15.0
        assert result["zero_review_listings"] == 1
        assert result["average_reviews_per_month"] == 3.0

    def test_counts_listings_with_zero_reviews(self):
        df = pd.DataFrame({
            "number_of_reviews": [0, 0, 5, 10],
            "reviews_per_month": [0.0, 0.0, 1.0, 2.0]
        })

        result = analyze_overall_reviews(df)

        assert result["zero_review_listings"] == 2

    def test_handles_missing_and_negative_review_counts(self):
        df = pd.DataFrame({
            "number_of_reviews": [10, None, -5, 20],
            "reviews_per_month": [2.0, 1.0, 3.0, 4.0]
        })

        result = analyze_overall_reviews(df)

        assert result["total_reviews"] == 30
        assert result["invalid_review_counts"] == 2

    def test_excludes_non_numeric_review_values(self):
        df = pd.DataFrame({
            "number_of_reviews": [10, "invalid", 20],
            "reviews_per_month": [1.0, 2.0, 3.0]
        })

        result = analyze_overall_reviews(df)

        assert result["total_reviews"] == 30
        assert result["invalid_review_counts"] == 1

    def test_excludes_infinite_review_counts(self):
        df = pd.DataFrame({
            "number_of_reviews": [10, np.inf, 20],
            "reviews_per_month": [1.0, 2.0, 3.0]
        })

        result = analyze_overall_reviews(df)

        assert result["total_reviews"] == 30
        assert result["invalid_review_counts"] == 1

    def test_excludes_fractional_total_review_counts(self):
        df = pd.DataFrame({
            "number_of_reviews": [10, 2.5, 20],
            "reviews_per_month": [1.0, 2.0, 3.0]
        })

        result = analyze_overall_reviews(df)

        assert result["total_reviews"] == 30
        assert result["invalid_review_counts"] == 1

    def test_handles_invalid_monthly_review_values(self):
        df = pd.DataFrame({
            "number_of_reviews": [10, 20, 30],
            "reviews_per_month": [2.0, -1.0, np.inf]
        })

        result = analyze_overall_reviews(df)

        assert result["average_reviews_per_month"] == 2.0
        assert result["invalid_monthly_reviews"] == 2

    def test_does_not_modify_original_dataframe(self):
        df = pd.DataFrame({
            "number_of_reviews": [10, None, 20],
            "reviews_per_month": [2.0, 1.0, 3.0]
        })

        original_df = df.copy(deep=True)

        analyze_overall_reviews(df)

        pd.testing.assert_frame_equal(df, original_df)

    def test_raises_key_error_when_required_column_is_missing(self):
        df = pd.DataFrame({
            "number_of_reviews": [10, 20]
        })

        with pytest.raises(KeyError):
            analyze_overall_reviews(df)

    def test_raises_type_error_for_invalid_input(self):
        with pytest.raises(TypeError):
            analyze_overall_reviews([10, 20, 30])

    def test_handles_empty_dataframe(self):
        df = pd.DataFrame({
            "number_of_reviews": [],
            "reviews_per_month": []
        })

        result = analyze_overall_reviews(df)

        assert result["total_listings"] == 0
        assert result["total_reviews"] == 0
        assert result["average_reviews_per_listing"] == 0.0
        assert result["zero_review_listings"] == 0
        assert result["average_reviews_per_month"] == 0.0
