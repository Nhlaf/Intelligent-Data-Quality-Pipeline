import json

from src.quality.integrated_report import (
    generate_integrated_report
)


def create_test_inputs():
    customer_metrics = {
        "total_records": 5,
        "valid_records": 4,
        "invalid_records": 1,
        "validation_success_rate": 80.0,
        "rejection_rate": 20.0,
        "completeness_rate": 100.0,
        "duplicate_count": 0
    }

    anomaly_results = {
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

    quality_rules = {
        "validation_success_threshold": 95.0,
        "completeness_threshold": 98.0,
        "maximum_duplicate_count": 0
    }

    return customer_metrics, anomaly_results, quality_rules


def test_integrated_report_created(tmp_path):
    metrics, anomalies, rules = create_test_inputs()

    report_path = generate_integrated_report(
        customer_metrics=metrics,
        anomaly_results=anomalies,
        quality_rules=rules,
        batch_id="batch001",
        output_dir=tmp_path
    )

    assert report_path.exists()


def test_integrated_report_content(tmp_path):
    metrics, anomalies, rules = create_test_inputs()

    report_path = generate_integrated_report(
        customer_metrics=metrics,
        anomaly_results=anomalies,
        quality_rules=rules,
        batch_id="batch002",
        output_dir=tmp_path
    )

    with report_path.open(encoding="utf-8") as file:
        report = json.load(file)

    assert report["batch_id"] == "batch002"

    assert (
        report["customer_data_quality"]["metrics"]["total_records"]
        == 5
    )

    assert (
        report["transaction_anomaly_detection"]["anomaly_count"]
        == 1
    )

    assert (
        report["customer_data_quality"]["quality_status"]
        == "FAIL"
    )


def test_integrated_report_timestamp(tmp_path):
    metrics, anomalies, rules = create_test_inputs()

    report_path = generate_integrated_report(
        customer_metrics=metrics,
        anomaly_results=anomalies,
        quality_rules=rules,
        batch_id="batch003",
        output_dir=tmp_path
    )

    with report_path.open(encoding="utf-8") as file:
        report = json.load(file)

    assert "generated_at" in report
    assert report["generated_at"]