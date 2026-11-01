"""
NYC Airbnb Data Summary Tool
CPSC620 - Group 1
Main application entry point.
"""

from pathlib import Path

from src.data_loader import load_data
from src.data_cleaning import clean_data
from src.price_analysis import calculate_price_summary
from src.neighbourhood_analysis import (
    average_prices_by_group,
    top_neighbourhoods_by_listings,
)
from src.availability_analysis import analyze_overall_availability
from src.review_analysis import analyze_overall_reviews


def section(title):
    print()
    print("=" * 66)
    print(f"  {title}")
    print("=" * 66)


def main():
    dataset_path = (
        Path(__file__).resolve().parent
        / "data"
        / "Airbnb_NYC.csv"
    )

    print()
    print("=" * 66)
    print("             NYC AIRBNB DATA SUMMARY TOOL")
    print("                CPSC620 - GROUP 1")
    print("=" * 66)

    # 1. Load and clean data
    raw = load_data(dataset_path)
    df = clean_data(raw)

    section("1. DATA QUALITY & PREPARATION")
    print(f"  Original listings : {len(raw):,}")
    print(f"  Cleaned listings  : {len(df):,}")
    print(f"  Removed records   : {len(raw) - len(df):,}")
    print(f"  Duplicate IDs     : {df['id'].duplicated().sum():,}")
    print(f"  Data retention    : {len(df)/len(raw)*100:.2f}%")

    # 2. Price analysis
    section("2. PRICE ANALYSIS")
    prices = calculate_price_summary(df)

    print(f"  Average price     : ${prices['average_price']:,.2f}")
    print(f"  Median price      : ${prices['median_price']:,.2f}")
    print(f"  Minimum price     : ${prices['minimum_price']:,.2f}")
    print(f"  Maximum price     : ${prices['maximum_price']:,.2f}")

    # 3. Neighbourhood analysis
    section("3. NEIGHBOURHOOD ANALYSIS")

    print("\n  Average prices by district (USD):\n")
    groups = average_prices_by_group(df)
    print(groups.to_string(index=False))

    print("\n  Top 5 neighbourhoods by listings:\n")
    top = top_neighbourhoods_by_listings(df, top_n=5)
    print(top.to_string(index=False))

    # 4. Availability analysis
    section("4. AVAILABILITY ANALYSIS")
    analyze_overall_availability(df)

    # 5. Review analysis
    section("5. REVIEW ANALYSIS")
    reviews = analyze_overall_reviews(df)

    print(f"  Total reviews       : {reviews['total_reviews']:,}")
    print(f"  Average per listing : {reviews['average_reviews_per_listing']:.2f}")
    print(f"  Zero-review listings: {reviews['zero_review_listings']:,}")
    print(f"  Average per month   : {reviews['average_reviews_per_month']:.2f}")

    section("EXECUTION COMPLETED SUCCESSFULLY")
    print("  All five analysis stages executed.")
    print("  Group 1 - University of Niagara Falls Canada")
    print()


if __name__ == "__main__":
    main()
