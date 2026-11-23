import pandas as pd

from src.quality.metrics import calculate_quality_metrics
from src.validation.validator import validate_customers


def test_quality_metrics():
    bronze_df = pd.DataFrame([
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
            "full_name": "Nomsa Khumalo",
            "email": "nomsa@example.com",
            "customer_status": "Closeds",
            "batch_id": "batch001",
            "ingestion_timestamp": "2026-11-23T10:00:00Z"
        }
    ])

    valid_df, invalid_df = validate_customers(bronze_df)

    metrics = calculate_quality_metrics(
        bronze_df,
        valid_df,
        invalid_df
    )

    assert metrics["total_records"] == 2
    assert metrics["valid_records"] == 1
    assert metrics["invalid_records"] == 1
    assert metrics["validation_success_rate"] == 50.0
    assert metrics["rejection_rate"] == 50.0
    assert metrics["completeness_rate"] == 100.0
    assert metrics["duplicate_count"] == 0