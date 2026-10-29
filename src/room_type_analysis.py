import pandas as pd


def analyze_prices_by_room_type(df):
    """
    Analyze Airbnb listing prices by room type.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing Airbnb listings with
        'room_type' and 'price' columns.

    Returns
    -------
    pandas.DataFrame
        Summary containing room type, average price,
        median price, and listing count.
    """
    required_columns = ["room_type", "price"]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Keep only the columns needed for this analysis.
    data = df[["room_type", "price"]].copy()

    # Convert prices to numeric values.
    data["price"] = pd.to_numeric(
        data["price"], errors="coerce"
    )

    # Remove rows with missing room types or prices.
    data = data.dropna(subset=["room_type", "price"])

    # Normalize room type names to avoid duplicate categories.
    data["room_type"] = (
        data["room_type"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # Remove empty room types and non-positive prices.
    data = data[data["room_type"] != ""]
    data = data[data["price"] > 0]

    if data.empty:
        raise ValueError(
            "No valid room types and positive prices "
            "available for analysis."
        )

    # Calculate statistics for each room type.
    summary = (
        data.groupby("room_type")
        .agg(
            average_price=("price", "mean"),
            median_price=("price", "median"),
            listing_count=("price", "count"),
        )
        .reset_index()
        .sort_values("room_type")
        .reset_index(drop=True)
    )

    return summary


if __name__ == "__main__":
    from pathlib import Path

    dataset_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "Airbnb_NYC.csv"
    )

    airbnb_df = pd.read_csv(dataset_path)

    results = analyze_prices_by_room_type(airbnb_df)

    print("NYC Airbnb Price Analysis by Room Type")
    print("-" * 60)
    print(results.to_string(index=False))
