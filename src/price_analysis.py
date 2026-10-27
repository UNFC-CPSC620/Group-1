
import pandas as pd


def calculate_price_summary(df):
    """
    Calculate descriptive statistics for Airbnb listing prices.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing Airbnb listings with a price column.

    Returns
    -------
    dict
        Dictionary containing the average, median, minimum,
        maximum, and number of valid prices.
    """
    if "price" not in df.columns:
        raise ValueError("The dataset must contain a 'price' column.")

    prices = pd.to_numeric(df["price"], errors="coerce")

    # Exclude missing, non-numeric, and negative prices.
    valid_prices = prices[prices.notna() & (prices >= 0)]

    if valid_prices.empty:
        raise ValueError("No valid prices available for analysis.")

    return {
        "average_price": valid_prices.mean(),
        "median_price": valid_prices.median(),
        "minimum_price": valid_prices.min(),
        "maximum_price": valid_prices.max(),
        "valid_price_count": int(valid_prices.count()),
    }
