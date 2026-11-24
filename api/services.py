import json
from pathlib import Path
from uuid import UUID


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REPORT_DIR = (
    PROJECT_ROOT / "data" / "gold" / "reports"
)

AI_ANALYSIS_DIR = (
    PROJECT_ROOT / "data" / "gold" / "ai_analysis"
)


def list_report_files() -> list[Path]:
    return sorted(
        REPORT_DIR.glob("integrated_report_*.json"),
        key=lambda path: path.stat().st_mtime_ns,
        reverse=True
    )


def read_report(report_path: Path) -> dict:
    with report_path.open(
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def get_latest_report() -> dict:
    reports = list_report_files()

    if not reports:
        raise FileNotFoundError(
            "No integrated reports found"
        )

    return read_report(reports[0])


def get_report_by_batch_id(batch_id: UUID) -> dict:
    report_path = (
        REPORT_DIR / f"integrated_report_{batch_id}.json"
    )

    if not report_path.is_file():
        raise FileNotFoundError(
            f"Report not found for batch: {batch_id}"
        )

    return read_report(report_path)


def get_customer_quality() -> dict:
    report = get_latest_report()

    return report["customer_data_quality"]


def get_transaction_anomalies() -> dict:
    report = get_latest_report()

    return report["transaction_anomaly_detection"]


def get_ai_analysis() -> dict:
    report = get_latest_report()

    batch_id = UUID(report["batch_id"])

    analysis_path = (
        AI_ANALYSIS_DIR / f"ai_analysis_{batch_id}.md"
    )

    if not analysis_path.is_file():
        raise FileNotFoundError(
            "AI analysis not found for this batch"
        )

    return {
        "batch_id": str(batch_id),
        "analysis": analysis_path.read_text(
            encoding="utf-8"
        )
    }