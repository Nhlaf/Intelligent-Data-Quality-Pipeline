import json
from datetime import datetime, timezone
from pathlib import Path

from src.quality.config import evaluate_quality


def generate_quality_report(
    metrics: dict,
    batch_id: str,
    output_dir: str | Path,
    rules: dict | None = None
) -> Path:

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if rules is None:
        rules = {
            "validation_success_threshold": 95.0,
            "completeness_threshold": 98.0,
            "maximum_duplicate_count": 0
        }

    quality_status = evaluate_quality(metrics, rules)

    report = {
        "report_type": "Customer Data Quality Report",
        "batch_id": batch_id,
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "metrics": metrics,
        "quality_rules": rules,
        "quality_status": quality_status
    }

    report_file = (
        output_path / f"quality_report_{batch_id}.json"
    )

    with report_file.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    return report_file