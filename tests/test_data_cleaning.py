
"""
Unit tests for TASK-03 / Issue #5.
NYC Airbnb Data Cleaning.
"""

import unittest

import pandas as pd

from src.data_cleaning import clean_data


class TestDataCleaning(unittest.TestCase):

    def make_row(self, **changes):
        row = {
            "id": 1,
            "name": "Apartment",
            "host_name": "Alex",
            "neighbourhood_group": "Brooklyn",
            "neighbourhood": "Williamsburg",
            "room_type": "Private room",
            "price": 100,
            "minimum_nights": 2,
            "availability_365": 30,
            "number_of_reviews": 0,
            "reviews_per_month": None,
            "last_review": None,
        }
        row.update(changes)
        return row

    def test_returns_dataframe(self):
        df = pd.DataFrame([self.make_row()])
        result = clean_data(df)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)

    def test_original_dataframe_unchanged(self):
        df = pd.DataFrame([self.make_row()])
        original = df.copy(deep=True)
        clean_data(df)
        pd.testing.assert_frame_equal(df, original)

    def test_missing_names(self):
        df = pd.DataFrame([
            self.make_row(name=None, host_name=" ")
        ])
        result = clean_data(df)
        self.assertEqual(
            result.iloc[0]["name"], "Unknown listing"
        )
        self.assertEqual(
            result.iloc[0]["host_name"], "Unknown host"
        )

    def test_whitespace_removal(self):
        df = pd.DataFrame([
            self.make_row(
                neighbourhood="  Williamsburg  ",
                room_type="  Private room  ",
            )
        ])
        result = clean_data(df)
        self.assertEqual(
            result.iloc[0]["neighbourhood"],
            "Williamsburg",
        )
        self.assertEqual(
            result.iloc[0]["room_type"], "Private room"
        )

    def test_missing_essential_fields(self):
        df = pd.DataFrame([
            self.make_row(id=1),
            self.make_row(id=2, neighbourhood=None),
            self.make_row(id=3, room_type=" "),
            self.make_row(id=None),
        ])
        result = clean_data(df)
        self.assertEqual(len(result), 1)

    def test_invalid_prices(self):
        df = pd.DataFrame([
            self.make_row(id=1, price=100),
            self.make_row(id=2, price=0),
            self.make_row(id=3, price=-10),
            self.make_row(id=4, price=None),
            self.make_row(id=5, price="invalid"),
            self.make_row(id=6, price=float("inf")),
        ])
        result = clean_data(df)
        self.assertEqual(result["id"].tolist(), [1])

    def test_invalid_minimum_nights(self):
        df = pd.DataFrame([
            self.make_row(id=1, minimum_nights=1),
            self.make_row(id=2, minimum_nights=0),
            self.make_row(id=3, minimum_nights=-2),
            self.make_row(id=4, minimum_nights=1.5),
            self.make_row(id=5, minimum_nights=None),
        ])
        result = clean_data(df)
        self.assertEqual(result["id"].tolist(), [1])

    def test_invalid_availability(self):
        df = pd.DataFrame([
            self.make_row(id=1, availability_365=0),
            self.make_row(id=2, availability_365=365),
            self.make_row(id=3, availability_365=-1),
            self.make_row(id=4, availability_365=366),
            self.make_row(id=5, availability_365=2.5),
            self.make_row(id=6, availability_365=None),
        ])
        result = clean_data(df)
        self.assertEqual(result["id"].tolist(), [1, 2])

    def test_exact_duplicates(self):
        row = self.make_row(id=1)
        df = pd.DataFrame([
            row,
            row.copy(),
            self.make_row(id=2),
        ])
        result = clean_data(df)
        self.assertEqual(len(result), 2)

    def test_repeated_ids_keep_first(self):
        df = pd.DataFrame([
            self.make_row(id=1, name="First"),
            self.make_row(id=1, name="Second"),
            self.make_row(id=2, name="Other"),
        ])
        result = clean_data(df)
        self.assertEqual(len(result), 2)
        self.assertEqual(result.iloc[0]["name"], "First")
        self.assertFalse(result["id"].duplicated().any())

    def test_review_missing_values(self):
        df = pd.DataFrame([
            self.make_row(
                id=1,
                number_of_reviews=0,
                reviews_per_month=None,
            ),
            self.make_row(
                id=2,
                number_of_reviews=2,
                reviews_per_month=None,
            ),
        ])
        result = clean_data(df)
        self.assertEqual(
            result.iloc[0]["reviews_per_month"], 0
        )
        self.assertTrue(
            pd.isna(result.iloc[1]["reviews_per_month"])
        )
        self.assertTrue(
            result["last_review"].isna().all()
        )

    def test_invalid_input_and_columns(self):
        with self.assertRaises(TypeError):
            clean_data("invalid input")

        with self.assertRaises(ValueError):
            clean_data(pd.DataFrame({"price": [100]}))


if __name__ == "__main__":
    unittest.main()
