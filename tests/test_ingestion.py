import pandas as pd
import pytest

from src.ingestion.csv_ingestion import load_csv


def test_load_valid_csv(tmp_path):
    """Check that a valid CSV loads correctly."""

    file = tmp_path / "customers.csv"

    file.write_text(
        "customer_id,full_name\n"
        "C001,Thabo Mokoena\n"
        "C002,Lerato Nkosi\n"
    )

    result = load_csv(file)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2


def test_missing_csv(tmp_path):
    """Check that a missing file raises an error."""

    file = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        load_csv(file)


def test_empty_csv(tmp_path):
    """Check that an empty CSV is rejected."""

    file = tmp_path / "empty.csv"
    file.write_text("")

    with pytest.raises(ValueError):
        load_csv(file)


def test_header_only_csv(tmp_path):
    """Check that a CSV with no records is rejected."""

    file = tmp_path / "headers.csv"
    file.write_text("customer_id,full_name\n")

    with pytest.raises(ValueError):
        load_csv(file)


def test_preserve_leading_zeros(tmp_path):
    """Check that customer IDs retain leading zeros."""

    file = tmp_path / "customers.csv"

    file.write_text(
        "customer_id,full_name\n"
        "0001,Thabo Mokoena\n"
    )

    result = load_csv(file)

    assert result.loc[0, "customer_id"] == "0001"