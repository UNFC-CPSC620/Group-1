import pandas as pd
import pytest

from src.data_validation import validate_data


def test_valid_data(capsys):
    """Verify that valid values are accepted."""
    df = pd.DataFrame({
        "price": [100, 200],
        "minimum_nights": [1, 3],
        "availability_365": [0, 365],
    })

    result = validate_data(df)
    output = capsys.readouterr().out

    assert len(result) == 2
    assert "Invalid price values: 0" in output
    assert "Invalid minimum_nights values: 0" in output
    assert "Invalid availability_365 values: 0" in output


def test_zero_negative_and_infinite_prices(capsys):
    """Verify that zero, negative, and infinite prices are invalid."""
    df = pd.DataFrame({
        "price": [100, 0, -10, float("inf"), float("-inf")],
        "minimum_nights": [1, 1, 1, 1, 1],
        "availability_365": [100, 100, 100, 100, 100],
    })

    validate_data(df)
    output = capsys.readouterr().out

    assert "Invalid price values: 4" in output


def test_missing_and_non_numeric_prices(capsys):
    """Verify that missing and non-numeric prices are invalid."""
    df = pd.DataFrame({
        "price": [100, None, "invalid"],
        "minimum_nights": [1, 1, 1],
        "availability_365": [100, 100, 100],
    })

    result = validate_data(df)
    output = capsys.readouterr().out

    assert "Invalid price values: 2" in output
    assert pd.isna(result.loc[1, "price"])
    assert pd.isna(result.loc[2, "price"])


def test_invalid_minimum_nights(capsys):
    """Verify invalid minimum-night values are identified."""
    df = pd.DataFrame({
        "price": [100] * 6,
        "minimum_nights": [1, 0, -2, 1.5, float("inf"), None],
        "availability_365": [100] * 6,
    })

    validate_data(df)
    output = capsys.readouterr().out

    assert "Invalid minimum_nights values: 5" in output


def test_invalid_availability(capsys):
    """Verify invalid availability values are identified."""
    df = pd.DataFrame({
        "price": [100] * 7,
        "minimum_nights": [1] * 7,
        "availability_365": [
            0,
            365,
            -1,
            366,
            20.5,
            float("inf"),
            None,
        ],
    })

    validate_data(df)
    output = capsys.readouterr().out

    assert "Invalid availability_365 values: 5" in output


def test_invalid_records_are_not_removed(capsys):
    """Verify that validation reports errors without removing rows."""
    df = pd.DataFrame({
        "price": [100, 0, -20],
        "minimum_nights": [1, 0, 2],
        "availability_365": [100, 400, 200],
    })

    result = validate_data(df)
    output = capsys.readouterr().out

    assert len(result) == len(df)
    assert result.loc[1, "price"] == 0
    assert result.loc[2, "price"] == -20
    assert "Invalid price values: 2" in output


def test_original_dataframe_is_unchanged():
    """Verify that validation does not modify the original DataFrame."""
    df = pd.DataFrame({
        "price": ["100", "0", "invalid"],
        "minimum_nights": ["1", "2", "3"],
        "availability_365": ["100", "200", "300"],
    })

    original = df.copy(deep=True)

    validate_data(df)

    pd.testing.assert_frame_equal(df, original)


def test_numeric_conversion():
    """Verify that numeric strings are converted to numeric values."""
    df = pd.DataFrame({
        "price": ["100", "200"],
        "minimum_nights": ["1", "2"],
        "availability_365": ["100", "200"],
    })

    result = validate_data(df)

    for column in ["price", "minimum_nights", "availability_365"]:
        assert pd.api.types.is_numeric_dtype(result[column])


def test_missing_required_column():
    """Verify that missing required columns raise ValueError."""
    df = pd.DataFrame({
        "price": [100],
        "minimum_nights": [1],
    })

    with pytest.raises(ValueError, match="availability_365"):
        validate_data(df)


def test_invalid_input_type():
    """Verify that non-DataFrame input raises TypeError."""
    with pytest.raises(TypeError, match="DataFrame"):
        validate_data([100, 200, 300])


def test_empty_dataframe(capsys):
    """Verify that an empty DataFrame is handled correctly."""
    df = pd.DataFrame(columns=[
        "price",
        "minimum_nights",
        "availability_365",
    ])

    result = validate_data(df)
    output = capsys.readouterr().out

    assert result.empty
    assert "Invalid price values: 0" in output
    assert "Invalid minimum_nights values: 0" in output
    assert "Invalid availability_365 values: 0" in output