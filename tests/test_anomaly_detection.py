import pandas as pd
import pytest

from src.quality.anomaly_detection import (
    detect_transaction_anomalies
)


def create_transaction_data():
    amounts = [
        150, 220, 180, 195, 175,
        210, 160, 230, 190, 205,
        185, 215, 170, 200, 225,
        155, 195, 180, 210, 95000
    ]

    return pd.DataFrame({
        "transaction_id": [
            f"T{i:03d}" for i in range(1, 21)
        ],
        "amount": amounts
    })


def test_anomaly_detection_output():
    df = create_transaction_data()

    result = detect_transaction_anomalies(df)

    assert len(result) == len(df)
    assert "anomaly_prediction" in result.columns
    assert "anomaly_score" in result.columns
    assert "anomaly_status" in result.columns


def test_extreme_transaction_detected():
    df = create_transaction_data()

    result = detect_transaction_anomalies(df)

    extreme_transaction = result[
        result["transaction_id"] == "T020"
    ]

    assert (
        extreme_transaction.iloc[0]["anomaly_status"]
        == "Anomaly"
    )


def test_missing_amount_column():
    df = pd.DataFrame({
        "transaction_id": ["T001", "T002"]
    })

    with pytest.raises(
        ValueError,
        match="Missing required column"
    ):
        detect_transaction_anomalies(df)


def test_invalid_amount():
    df = pd.DataFrame({
        "amount": [100, "invalid", 200]
    })

    with pytest.raises(
        ValueError,
        match="valid numbers"
    ):
        detect_transaction_anomalies(df)


def test_empty_transactions():
    df = pd.DataFrame({
        "amount": []
    })

    with pytest.raises(
        ValueError,
        match="empty data"
    ):
        detect_transaction_anomalies(df)