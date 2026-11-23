import json

from src.quality.report import generate_quality_report


def test_generate_quality_report(tmp_path):
    metrics = {
        "total_records": 5,
        "valid_records": 4,
        "invalid_records": 1,
        "validation_success_rate": 80.0,
        "rejection_rate": 20.0,
        "completeness_rate": 100.0,
        "duplicate_count": 0
    }

    report_path = generate_quality_report(
        metrics=metrics,
        batch_id="batch001",
        output_dir=tmp_path
    )

    assert report_path.exists()

    with open(report_path, encoding="utf-8") as file:
        report = json.load(file)

    assert report["batch_id"] == "batch001"
    assert report["metrics"]["total_records"] == 5
    assert report["quality_status"] == "FAIL"


def test_quality_report_pass(tmp_path):
    metrics = {
        "total_records": 100,
        "valid_records": 98,
        "invalid_records": 2,
        "validation_success_rate": 98.0,
        "rejection_rate": 2.0,
        "completeness_rate": 100.0,
        "duplicate_count": 0
    }

    report_path = generate_quality_report(
        metrics=metrics,
        batch_id="batch002",
        output_dir=tmp_path
    )

    with open(report_path, encoding="utf-8") as file:
        report = json.load(file)

    assert report["quality_status"] == "PASS"


def test_report_contains_timestamp(tmp_path):
    metrics = {
        "total_records": 5,
        "valid_records": 5,
        "invalid_records": 0,
        "validation_success_rate": 100.0,
        "rejection_rate": 0.0,
        "completeness_rate": 100.0,
        "duplicate_count": 0
    }

    report_path = generate_quality_report(
        metrics=metrics,
        batch_id="batch003",
        output_dir=tmp_path
    )

    with open(report_path, encoding="utf-8") as file:
        report = json.load(file)

    assert "generated_at" in report
    assert report["generated_at"]
    assert report["quality_status"] == "PASS"