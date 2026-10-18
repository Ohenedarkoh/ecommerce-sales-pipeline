
import pandas as pd
import pytest
from src.utils.data_utils import (convert_type,convert_datetype,date_summary,profile_col,load_csv)

# Checks that a column's data type changes without changing the original data.
def test_convert_type():
    postal_codes = pd.Series([12345, 54321, 67890])

    converted_postal_codes = convert_type(postal_codes, 'str')

    assert converted_postal_codes.dtype == object
    assert converted_postal_codes.tolist() == ['12345', '54321', '67890']
    assert postal_codes.dtype == 'int64'


# Checks that a date string is converted to the correct date.
def test_convert_datetype():
    result = convert_datetype('25/12/2025')
    assert str(result.date()) == '2025-12-25'

# Checks that the latest date is returned.
def test_date_summary_latest():
    dates = pd.to_datetime(['2025-01-01', '2025-12-31', '2025-06-15'])
    assert date_summary(dates, 'latest') == pd.Timestamp('2025-12-31')

# Checks that the oldest date is returned.
def test_date_summary_oldest():
    dates = pd.to_datetime(['2025-01-01', '2025-12-31', '2025-06-15'])
    assert date_summary(dates, 'oldest') == pd.Timestamp('2025-01-01')



# Checks missing values, unique values, and duplicate rows in a DataFrame.
def test_profile_col():
    df = pd.DataFrame({'Sales': [100, 200, 200, None]})
    result = profile_col(df)

    assert result.loc['Sales', 'Missing values'] == 1
    assert result.loc['Sales', 'Unique values'] == 2
    assert result.loc['Sales', 'duplicate'] == 1


# Checks that a semicolon-separated CSV loads with the correct columns and values.
def test_load_csv(tmp_path):
    file_path = tmp_path / "sample.csv"
    file_path.write_text(
        "Product ID;Category\nP001;Furniture\nP002;Technology\n",
        encoding="latin1",
    )

    result = load_csv("sample.csv", str(tmp_path))

    assert list(result.columns) == ["Product ID", "Category"]
    assert len(result) == 2
    assert result.loc[0, "Product ID"] == "P001"
    assert result.loc[1, "Category"] == "Technology"



# Checks that loading a file that does not exist raises an error.
def test_load_csv_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_csv("missing.csv", str(tmp_path))



# Checks that an invalid date raises a ValueError.
def test_convert_datetype_invalid_date():
    with pytest.raises(ValueError):
        convert_datetype("31/02/2025")

# Checks that the percentage of missing values is calculated correctly
def test_profile_col_missing_percentage():
    df = pd.DataFrame({"Sales": [100, None, 200, None]})

    result = profile_col(df)

    assert result.loc["Sales", "Missing percentage"] == 50.0


# Checks that the column's data type is reported correctly.
def test_profile_col_data_types():
    df = pd.DataFrame({"Sales": [100, 200]})

    result = profile_col(df)

    assert result.loc["Sales", "Data types"] == df["Sales"].dtype


# Checks what happens when an unsupported operation is passed.
def test_date_summary_invalid_operation():
    dates = pd.to_datetime(["2025-01-01", "2025-12-31"])

    assert date_summary(dates, "invalid") == "invalid"
