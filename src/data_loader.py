import pandas as pd
from pathlib import Path


def load_data(file_path):
    """
    Load the NYC Airbnb dataset from a CSV file.

    Parameters
    ----------
    file_path : str or Path
        Path to the CSV dataset.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing Airbnb listings.
    """
    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    df = pd.read_csv(file_path)

    return df

def display_dataset_info(df):
    """
    Display the dataset dimensions and column names.
    """
    print("NYC Airbnb Dataset Information")
    print("-" * 40)

    print(f"Number of rows: {df.shape[0]}")
    print(f"Number of columns: {df.shape[1]}")

    print("\nColumn names:")
    for column in df.columns:
        print(f"- {column}")


if __name__ == "__main__":
    dataset_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "Airbnb_NYC.csv"
    )

    airbnb_df = load_data(dataset_path)

    display_dataset_info(airbnb_df)

    print("\nFirst five rows:")
    print(airbnb_df.head())
