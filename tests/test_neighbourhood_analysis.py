
import unittest
import pandas as pd

from src.neighbourhood_analysis import (
    clean_price_data,
    average_prices_by_group,
    average_prices_by_neighbourhood,
    top_neighbourhoods_by_listings,
)


class TestNeighbourhoodAnalysis(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({
            "neighbourhood_group": [
                "Manhattan", "manhattan", "Brooklyn",
                "Queens", "Bronx", "Manhattan",
                "Brooklyn", "Staten Island"
            ],
            "neighbourhood": [
                "Chelsea", "Chelsea", "Williamsburg",
                "Astoria", "Fordham", "Chelsea",
                "Williamsburg", "St. George"
            ],
            "price": [
                100, 200, 150, 0, None,
                -5, float("inf"), "abc"
            ]
        })

    def test_invalid_prices_removed(self):
        result = clean_price_data(self.df)
        self.assertEqual(len(result), 3)
        self.assertEqual(
            sorted(result["price"].tolist()),
            [100, 150, 200]
        )

    def test_group_normalization(self):
        result = average_prices_by_group(self.df)
        self.assertEqual(len(result), 2)

        manhattan = result.loc[
            result["neighbourhood_group"] == "Manhattan"
        ].iloc[0]

        self.assertEqual(manhattan["average_price"], 150)
        self.assertEqual(manhattan["listing_count"], 2)

    def test_neighbourhood_averages(self):
        result = average_prices_by_neighbourhood(self.df)

        chelsea = result.loc[
            result["neighbourhood"] == "Chelsea"
        ].iloc[0]

        self.assertEqual(chelsea["average_price"], 150)
        self.assertEqual(chelsea["listing_count"], 2)

    def test_top_neighbourhoods(self):
        result = top_neighbourhoods_by_listings(
            self.df, top_n=2
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(
            result.iloc[0]["neighbourhood"],
            "Chelsea"
        )
        self.assertEqual(
            result.iloc[0]["listing_count"], 2
        )

    def test_missing_price_column(self):
        with self.assertRaises(ValueError):
            clean_price_data(
                self.df.drop(columns=["price"])
            )

    def test_invalid_top_n(self):
        for value in [0, -1, True, 1.5, "2"]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    top_neighbourhoods_by_listings(
                        self.df, top_n=value
                    )

    def test_original_data_unchanged(self):
        original = self.df.copy(deep=True)

        average_prices_by_group(self.df)

        pd.testing.assert_frame_equal(
            self.df, original
        )

    def test_dataframe_return_types(self):
        functions = [
            average_prices_by_group,
            average_prices_by_neighbourhood,
            top_neighbourhoods_by_listings
        ]

        for function in functions:
            with self.subTest(function=function.__name__):
                self.assertIsInstance(
                    function(self.df), pd.DataFrame
                )


if __name__ == "__main__":
    unittest.main()
