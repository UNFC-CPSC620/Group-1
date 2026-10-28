
"""
Regression tests for neighbourhood name normalization.

TASK-11 / Issue #15
"""

import unittest
import pandas as pd

from src.neighbourhood_analysis import (
    average_prices_by_neighbourhood,
    top_neighbourhoods_by_listings,
)


class TestNeighbourhoodNormalization(unittest.TestCase):

    def test_case_insensitive_neighbourhood_names(self):
        # Same neighbourhoods with different capitalization.
        df = pd.DataFrame({
            "neighbourhood_group": [
                "Manhattan", "Manhattan",
                "Brooklyn", "Brooklyn"
            ],
            "neighbourhood": [
                "Tribeca", "tribeca",
                "Red Hook", "red hook"
            ],
            "price": [100, 300, 80, 120]
        })

        # Verify average prices and merged listing counts.
        averages = average_prices_by_neighbourhood(df)

        self.assertEqual(len(averages), 2)

        by_name = averages.set_index("neighbourhood")

        self.assertEqual(
            by_name.loc["Tribeca", "listing_count"], 2
        )
        self.assertEqual(
            by_name.loc["Tribeca", "average_price"], 200
        )
        self.assertEqual(
            by_name.loc["Red Hook", "listing_count"], 2
        )
        self.assertEqual(
            by_name.loc["Red Hook", "average_price"], 100
        )

        # Verify ranking also merges equivalent names.
        ranking = top_neighbourhoods_by_listings(df)

        self.assertEqual(len(ranking), 2)
        self.assertEqual(
            sorted(ranking["listing_count"].tolist()),
            [2, 2]
        )


if __name__ == "__main__":
    unittest.main()
