
"""
Unit tests for TASK-02 / Issue #3.
Missing values and duplicate detection.
"""

import unittest
import pandas as pd

from src.missing_duplicates import (
    missing_values_report,
    find_duplicate_rows,
    duplicate_summary,
)


class TestMissingDuplicates(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({
            "id": [1, 1, 2, 3, 4],
            "name": ["A", "A", " ", "", None],
            "price": [100, 100, 0, None, 40],
        })

    def test_missing_values(self):
        report = missing_values_report(self.df)
        report = report.set_index("column")

        self.assertEqual(
            report.loc["name", "missing_count"], 3
        )
        self.assertEqual(
            report.loc["price", "missing_count"], 1
        )

    def test_missing_percentages(self):
        report = missing_values_report(self.df)
        report = report.set_index("column")

        self.assertEqual(
            report.loc["name", "missing_percentage"], 60
        )
        self.assertEqual(
            report.loc["price", "missing_percentage"], 20
        )

    def test_zero_is_not_missing(self):
        report = missing_values_report(self.df)
        price_row = report.set_index("column").loc["price"]

        self.assertEqual(price_row["missing_count"], 1)

    def test_duplicate_rows(self):
        duplicates = find_duplicate_rows(self.df)

        self.assertEqual(len(duplicates), 2)
        self.assertTrue((duplicates["id"] == 1).all())

    def test_duplicate_summary(self):
        summary = duplicate_summary(self.df)
        results = dict(zip(
            summary["metric"], summary["count"]
        ))

        self.assertEqual(results["total_rows"], 5)
        self.assertEqual(results["extra_duplicate_rows"], 1)
        self.assertEqual(
            results["rows_in_duplicate_groups"], 2
        )
        self.assertEqual(results["extra_duplicate_ids"], 1)

    def test_missing_ids_are_not_duplicates(self):
        df = pd.DataFrame({
            "id": [None, None, 2, 2],
            "name": ["A", "B", "C", "D"],
        })

        summary = duplicate_summary(df)
        results = dict(zip(
            summary["metric"], summary["count"]
        ))

        self.assertEqual(results["extra_duplicate_ids"], 1)

    def test_empty_dataframe(self):
        df = pd.DataFrame(columns=["id", "name"])

        report = missing_values_report(df)
        summary = duplicate_summary(df)

        self.assertTrue(
            (report["missing_percentage"] == 0).all()
        )
        self.assertEqual(
            summary.loc[
                summary["metric"] == "total_rows", "count"
            ].iloc[0], 0
        )

    def test_missing_id_column(self):
        df = pd.DataFrame({"name": ["A", "B"]})
        summary = duplicate_summary(df)

        self.assertNotIn(
            "extra_duplicate_ids",
            summary["metric"].tolist()
        )

    def test_invalid_input(self):
        for function in (
            missing_values_report,
            find_duplicate_rows,
            duplicate_summary,
        ):
            with self.subTest(function=function.__name__):
                with self.assertRaises(TypeError):
                    function("invalid input")

    def test_original_dataframe_unchanged(self):
        original = self.df.copy(deep=True)

        missing_values_report(self.df)
        find_duplicate_rows(self.df)
        duplicate_summary(self.df)

        pd.testing.assert_frame_equal(self.df, original)


if __name__ == "__main__":
    unittest.main()
