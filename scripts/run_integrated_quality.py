from pathlib import Path

import pandas as pd

from src.quality.anomaly_detection import (
    detect_transaction_anomalies
)
from src.quality.config import load_quality_rules
from src.quality.integrated_report import (
    generate_integrated_report
)
from src.quality.metrics import calculate_quality_metrics
from src.validation.validator import validate_customers


PROJECT_ROOT = Path(__file__).resolve().parents[1]

BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"

TRANSACTION_FILE = (
    PROJECT_ROOT / "data" / "raw" / "transactions.csv"
)

CONFIG_FILE = (
    PROJECT_ROOT / "configs" / "quality_rules.json"
)

REPORT_DIR = (
    PROJECT_ROOT / "data" / "gold" / "reports"
)


def main():
    print("Starting integrated data quality pipeline...")

    # STEP 1: Load customer data
    bronze_files = list(
        BRONZE_DIR.glob("customers_*.parquet")
    )

    if not bronze_files:
        raise FileNotFoundError(
            "No customer Bronze files found"
        )

    latest_file = max(
        bronze_files,
        key=lambda path: path.stat().st_mtime_ns
    )

    customer_df = pd.read_parquet(latest_file)

    batch_id = latest_file.stem.removeprefix("customers_")

    # STEP 2: Validate customer data
    valid_df, invalid_df = validate_customers(
        customer_df
    )

    # STEP 3: Calculate customer quality metrics
    customer_metrics = calculate_quality_metrics(
        customer_df,
        valid_df,
        invalid_df
    )

    # STEP 4: Load transaction data
    transaction_df = pd.read_csv(
        TRANSACTION_FILE,
        dtype={
            "transaction_id": str,
            "customer_id": str
        }
    )

    # STEP 5: Detect transaction anomalies
    anomaly_df = detect_transaction_anomalies(
        transaction_df
    )

    anomaly_records = anomaly_df[
        anomaly_df["anomaly_status"] == "Anomaly"
    ]

    # STEP 6: Summarise anomaly results
    anomaly_results = {
        "total_transactions": int(len(anomaly_df)),
        "anomaly_count": int(len(anomaly_records)),
        "anomaly_rate": round(
            len(anomaly_records) / len(anomaly_df) * 100,
            2
        ),
        "flagged_transactions": [
            {
                "transaction_id": str(row["transaction_id"]),
                "customer_id": str(row["customer_id"]),
                "amount": float(row["amount"]),
                "anomaly_score": float(row["anomaly_score"])
            }
            for _, row in anomaly_records.iterrows()
        ]
    }

    # STEP 7: Load quality rules
    quality_rules = load_quality_rules(CONFIG_FILE)

    # STEP 8: Generate integrated JSON report
    report_path = generate_integrated_report(
        customer_metrics=customer_metrics,
        anomaly_results=anomaly_results,
        quality_rules=quality_rules,
        batch_id=batch_id,
        output_dir=REPORT_DIR
    )

    print("\nINTEGRATED DATA QUALITY REPORT")
    print("--------------------------------")

    print("\nCustomer Quality Metrics:")

    for metric, value in customer_metrics.items():
        print(f"{metric}: {value}")

    print("\nTransaction Anomaly Results:")

    print(
        f"Total transactions: "
        f"{anomaly_results['total_transactions']}"
    )

    print(
        f"Anomalies detected: "
        f"{anomaly_results['anomaly_count']}"
    )

    print(
        f"Anomaly rate: "
        f"{anomaly_results['anomaly_rate']}%"
    )

    print(f"\nReport saved: {report_path}")

    print("\nIntegrated pipeline completed!")


if __name__ == "__main__":
    main()