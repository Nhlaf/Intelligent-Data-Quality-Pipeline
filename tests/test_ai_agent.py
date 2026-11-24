import pytest

from src.ai_agent.data_quality_agent import (
    analyze_data_quality,
    prepare_report_context
)


def create_test_report():
    return {
        "customer_data_quality": {
            "metrics": {
                "total_records": 5,
                "valid_records": 4,
                "invalid_records": 1,
                "validation_success_rate": 80.0,
                "rejection_rate": 20.0,
                "completeness_rate": 100.0,
                "duplicate_count": 0
            },
            "quality_rules": {
                "validation_success_threshold": 95.0,
                "completeness_threshold": 98.0,
                "maximum_duplicate_count": 0
            },
            "quality_status": "FAIL"
        },
        "transaction_anomaly_detection": {
            "total_transactions": 20,
            "anomaly_count": 1,
            "anomaly_rate": 5.0,
            "flagged_transactions": [
                {
                    "transaction_id": "T020",
                    "customer_id": "C004",
                    "amount": 95000.0,
                    "anomaly_score": -0.2
                }
            ]
        }
    }


def test_prepare_report_context():
    report = create_test_report()

    context = prepare_report_context(report)

    assert context["quality_status"] == "FAIL"

    assert (
        context["customer_metrics"]["total_records"] == 5
    )

    assert (
        context["transaction_summary"]["anomaly_count"] == 1
    )


def test_sensitive_transaction_details_excluded():
    report = create_test_report()

    context = prepare_report_context(report)

    assert "flagged_transactions" not in context[
        "transaction_summary"
    ]

    assert "customer_id" not in str(context)
    assert "C004" not in str(context)
    assert "T020" not in str(context)


def test_missing_api_key(monkeypatch):
    monkeypatch.delenv(
        "GROQ_API_KEY",
        raising=False
    )

    report = create_test_report()

    with pytest.raises(
        ValueError,
        match="GROQ_API_KEY is missing"
    ):
        analyze_data_quality(report)