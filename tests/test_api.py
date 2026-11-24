import json

import pytest

from fastapi.testclient import TestClient

from api.main import app
from api import services


client = TestClient(app)

BATCH_ID = "e36e6c34-f43a-4801-b7a4-55a61c3229e8"


@pytest.fixture
def sample_report(tmp_path, monkeypatch):

    report_dir = tmp_path / "reports"
    analysis_dir = tmp_path / "ai_analysis"

    report_dir.mkdir()
    analysis_dir.mkdir()

    monkeypatch.setattr(
        services, "REPORT_DIR", report_dir
    )

    monkeypatch.setattr(
        services, "AI_ANALYSIS_DIR", analysis_dir
    )

    report = {
        "report_type": "Integrated Data Quality Report",
        "batch_id": BATCH_ID,
        "generated_at": "2026-11-24T10:00:00+00:00",
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

    report_file = (
        report_dir / f"integrated_report_{BATCH_ID}.json"
    )

    report_file.write_text(
        json.dumps(report),
        encoding="utf-8"
    )

    analysis_file = (
        analysis_dir / f"ai_analysis_{BATCH_ID}.md"
    )

    analysis_file.write_text(
        "Review invalid records and flagged transactions.",
        encoding="utf-8"
    )

    return report


def test_root():
    response = client.get("/")

    assert response.status_code == 200


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_list_reports(sample_report):
    response = client.get("/api/v1/reports")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_latest_report(sample_report):
    response = client.get("/api/v1/reports/latest")

    assert response.status_code == 200
    assert response.json()["batch_id"] == BATCH_ID


def test_report_by_batch_id(sample_report):
    response = client.get(
        f"/api/v1/reports/{BATCH_ID}"
    )

    assert response.status_code == 200
    assert response.json()["batch_id"] == BATCH_ID


def test_customer_quality(sample_report):
    response = client.get("/api/v1/quality")

    assert response.status_code == 200
    assert response.json()["quality_status"] == "FAIL"
    assert response.json()["metrics"]["total_records"] == 5


def test_transaction_anomalies(sample_report):
    response = client.get("/api/v1/anomalies")

    assert response.status_code == 200
    assert response.json()["anomaly_count"] == 1


def test_ai_analysis(sample_report):
    response = client.get("/api/v1/ai-analysis")

    assert response.status_code == 200
    assert "Review invalid records" in response.json()["analysis"]


def test_report_not_found(sample_report):
    response = client.get(
        "/api/v1/reports/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404


def test_invalid_batch_id():
    response = client.get(
        "/api/v1/reports/invalid-id"
    )

    assert response.status_code == 422


def test_no_reports(tmp_path, monkeypatch):
    monkeypatch.setattr(
        services,
        "REPORT_DIR",
        tmp_path
    )

    response = client.get("/api/v1/reports/latest")

    assert response.status_code == 404