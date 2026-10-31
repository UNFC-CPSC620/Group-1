import numpy as np
import pandas as pd


def validate_data(df):
    """
    Validate numeric data in the NYC Airbnb dataset.

    This function converts the required columns to numeric values,
    identifies invalid entries, and prints a validation summary.

    Invalid records are reported but are not removed or corrected.
    Data cleaning is handled separately by the data_cleaning module.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing Airbnb listings.

    Returns
    -------
    pandas.DataFrame
        A copy of the input DataFrame with the required numeric
        columns converted to numeric types. Invalid values remain
        in the returned DataFrame.

    Raises
    ------
    TypeError
        If the input is not a pandas DataFrame.
    ValueError
        If any required column is missing.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    df = df.copy()

    print("NYC Airbnb Data Validation")
    print("-" * 40)

    # 1. Inspect column data types
    print("\nColumn data types:")
    print(df.dtypes)

    # 2. Validate required columns
    required_columns = [
        "price",
        "minimum_nights",
        "availability_365",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # 3. Convert required columns to numeric types
    for column in required_columns:
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        )

    # 4. Identify invalid values
    invalid_price = (
        df["price"].isna()
        | ~np.isfinite(df["price"])
        | (df["price"] <= 0)
    )

    invalid_minimum_nights = (
        df["minimum_nights"].isna()
        | ~np.isfinite(df["minimum_nights"])
        | (df["minimum_nights"] < 1)
        | (df["minimum_nights"] % 1 != 0)
    )

    invalid_availability = (
        df["availability_365"].isna()
        | ~np.isfinite(df["availability_365"])
        | ~df["availability_365"].between(0, 365)
        | (df["availability_365"] % 1 != 0)
    )

    print("\nValidation results:")
    print(f"Invalid price values: {invalid_price.sum()}")
    print(
        "Invalid minimum_nights values: "
        f"{invalid_minimum_nights.sum()}"
    )
    print(
        "Invalid availability_365 values: "
        f"{invalid_availability.sum()}"
    )

    return df


if __name__ == "__main__":
    from pathlib import Path
    from data_loader import load_data

    dataset_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "Airbnb_NYC.csv"
    )

    airbnb_df = load_data(dataset_path)
    validated_df = validate_data(airbnb_df)