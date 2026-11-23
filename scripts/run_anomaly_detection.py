from pathlib import Path

import pandas as pd

from src.quality.anomaly_detection import (
    detect_transaction_anomalies
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT / "data" / "raw" / "transactions.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT / "data" / "gold" / "anomalies"
)


def main():
    print("Starting transaction anomaly detection...")

    if not INPUT_FILE.is_file():
        raise FileNotFoundError(
            f"Transaction file not found: {INPUT_FILE}"
        )

    df = pd.read_csv(
        INPUT_FILE,
        dtype={"transaction_id": str, "customer_id": str}
    )

    results = detect_transaction_anomalies(df)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        OUTPUT_DIR / "transaction_anomalies.parquet"
    )

    results.to_parquet(
        output_file,
        index=False
    )

    print("\nANOMALY DETECTION REPORT")
    print("---------------------------")

    print(f"Total transactions: {len(results)}")

    anomaly_count = (
        results["anomaly_status"] == "Anomaly"
    ).sum()

    print(f"Anomalies detected: {anomaly_count}")

    print("\nFlagged transactions:")

    flagged = results[
        results["anomaly_status"] == "Anomaly"
    ]

    print(
        flagged[
            [
                "transaction_id",
                "customer_id",
                "amount",
                "anomaly_score",
                "anomaly_status"
            ]
        ].to_string(index=False)
    )

    print(f"\nResults saved: {output_file}")
    print("\nAnomaly detection completed!")


if __name__ == "__main__":
    main()