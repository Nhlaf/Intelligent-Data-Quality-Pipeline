import json
from datetime import datetime, timezone
from pathlib import Path

from src.quality.config import evaluate_quality


def generate_integrated_report(
    customer_metrics: dict,
    anomaly_results: dict,
    quality_rules: dict,
    batch_id: str,
    output_dir: str | Path
) -> Path:
    """
    Generate a combined customer quality and
    transaction anomaly detection report.
    """

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    quality_status = evaluate_quality(
        customer_metrics,
        quality_rules
    )

    report = {
        "report_type": "Integrated Data Quality Report",
        "batch_id": batch_id,
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "customer_data_quality": {
            "metrics": customer_metrics,
            "quality_rules": quality_rules,
            "quality_status": quality_status
        },
        "transaction_anomaly_detection": anomaly_results
    }

    report_file = (
        output_path / f"integrated_report_{batch_id}.json"
    )

    with report_file.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(report, file, indent=4)

    return report_file