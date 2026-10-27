
import unittest
import pandas as pd

from src.neighbourhood_group_analysis import (
    summarize_listings_by_neighbourhood_group
)


class TestNeighbourhoodGroupAnalysis(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({
            "neighbourhood_group": [
                "Manhattan",
                "MANHATTAN",
                "Brooklyn",
                " brooklyn ",
                "Queens",
                None,
                ""
            ],
            "price": [
                100, 200, 0, None, -5, 150, 300
            ]
        })

    def test_listing_counts(self):
        result = summarize_listings_by_neighbourhood_group(
            self.df
        )

        counts = result.set_index(
            "neighbourhood_group"
        )["listing_count"]

        self.assertEqual(counts["Manhattan"], 2)
        self.assertEqual(counts["Brooklyn"], 2)
        self.assertEqual(counts["Queens"], 1)

    def test_percentages(self):
        result = summarize_listings_by_neighbourhood_group(
            self.df
        )

        percentages = result.set_index(
            "neighbourhood_group"
        )["percentage"]

        self.assertEqual(percentages["Manhattan"], 40)
        self.assertEqual(percentages["Brooklyn"], 40)
        self.assertEqual(percentages["Queens"], 20)
        self.assertAlmostEqual(
            result["percentage"].sum(), 100
        )

    def test_missing_group_names(self):
        result = summarize_listings_by_neighbourhood_group(
            self.df
        )

        self.assertEqual(
            result["listing_count"].sum(), 5
        )

    def test_invalid_input(self):
        with self.assertRaises(TypeError):
            summarize_listings_by_neighbourhood_group(
                "invalid input"
            )

    def test_missing_column(self):
        with self.assertRaises(ValueError):
            summarize_listings_by_neighbourhood_group(
                pd.DataFrame({"price": [100, 200]})
            )

    def test_original_data_unchanged(self):
        original = self.df.copy(deep=True)

        summarize_listings_by_neighbourhood_group(
            self.df
        )

        pd.testing.assert_frame_equal(
            self.df, original
        )

    def test_empty_dataframe(self):
        df = pd.DataFrame({
            "neighbourhood_group": []
        })

        result = summarize_listings_by_neighbourhood_group(
            df
        )

        self.assertTrue(result.empty)
        self.assertEqual(
            list(result.columns),
            [
                "neighbourhood_group",
                "listing_count",
                "percentage"
            ]
        )


if __name__ == "__main__":
    unittest.main()
