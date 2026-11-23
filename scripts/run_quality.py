from pathlib import Path

import pandas as pd

from src.quality.config import (
    evaluate_quality,
    load_quality_rules
)
from src.quality.metrics import calculate_quality_metrics
from src.quality.report import generate_quality_report
from src.validation.validator import validate_customers


PROJECT_ROOT = Path(__file__).resolve().parents[1]

BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"
REPORT_DIR = PROJECT_ROOT / "data" / "gold" / "reports"
CONFIG_FILE = PROJECT_ROOT / "configs" / "quality_rules.json"


def main():
    print("Starting data quality assessment...")

    bronze_files = list(
        BRONZE_DIR.glob("customers_*.parquet")
    )

    if not bronze_files:
        raise FileNotFoundError("No Bronze files found")

    latest_file = max(
        bronze_files,
        key=lambda path: path.stat().st_mtime_ns
    )

    print(f"Reading: {latest_file.name}")

    bronze_df = pd.read_parquet(latest_file)

    valid_df, invalid_df = validate_customers(bronze_df)

    metrics = calculate_quality_metrics(
        bronze_df,
        valid_df,
        invalid_df
    )

    rules = load_quality_rules(CONFIG_FILE)

    quality_status = evaluate_quality(metrics, rules)

    batch_id = latest_file.stem.removeprefix("customers_")

    report_path = generate_quality_report(
        metrics=metrics,
        batch_id=batch_id,
        output_dir=REPORT_DIR,
        rules=rules
    )

    print("\nDATA QUALITY REPORT")
    print("---------------------------")

    for metric, value in metrics.items():
        print(f"{metric}: {value}")

    print(f"\nQuality Status: {quality_status}")
    print(f"Report saved: {report_path}")

    print("\nQuality assessment completed!")


if __name__ == "__main__":
    main()