import pandas as pd
import pytest

from src.validation.validator import validate_customers


def create_test_data():
    return pd.DataFrame([
        {
            "customer_id": "C001",
            "full_name": "Thabo Mokoena",
            "email": "thabo@example.com",
            "customer_status": "Active",
            "batch_id": "batch001",
            "ingestion_timestamp": "2026-11-23T10:00:00Z"
        },
        {
            "customer_id": "C002",
            "full_name": "Lerato Nkosi",
            "email": "lerato@example.com",
            "customer_status": "Closeds",
            "batch_id": "batch001",
            "ingestion_timestamp": "2026-11-23T10:00:00Z"
        }
    ])


def test_valid_records():
    df = create_test_data()

    valid_df, invalid_df = validate_customers(df)

    assert len(valid_df) == 1
    assert valid_df.iloc[0]["customer_id"] == "C001"


def test_invalid_records():
    df = create_test_data()

    valid_df, invalid_df = validate_customers(df)

    assert len(invalid_df) == 1
    assert invalid_df.iloc[0]["customer_id"] == "C002"


def test_rejection_reason():
    df = create_test_data()

    _, invalid_df = validate_customers(df)

    assert "rejection_reason" in invalid_df.columns
    assert "Active" in invalid_df.iloc[0]["rejection_reason"]


def test_all_valid_records():
    df = create_test_data()

    df["customer_status"] = "Active"

    valid_df, invalid_df = validate_customers(df)

    assert len(valid_df) == 2
    assert len(invalid_df) == 0


def test_all_invalid_records():
    df = create_test_data()

    df["customer_status"] = "Unknown"

    valid_df, invalid_df = validate_customers(df)

    assert len(valid_df) == 0
    assert len(invalid_df) == 2


def test_metadata_preserved():
    df = create_test_data()

    valid_df, _ = validate_customers(df)

    assert valid_df.iloc[0]["batch_id"] == "batch001"
    assert (
        valid_df.iloc[0]["ingestion_timestamp"]
        == "2026-11-23T10:00:00Z"
    )


def test_duplicate_customer_id():
    df = create_test_data()

    df["customer_status"] = "Active"
    df.loc[1, "customer_id"] = "C001"

    valid_df, invalid_df = validate_customers(df)

    assert len(valid_df) == 1
    assert len(invalid_df) == 1

    assert "Duplicate customer ID" in (
        invalid_df.iloc[0]["rejection_reason"]
    )


def test_missing_required_column():
    df = create_test_data()

    df = df.drop(columns=["email"])

    with pytest.raises(
        ValueError,
        match="Missing required columns"
    ):
        validate_customers(df)