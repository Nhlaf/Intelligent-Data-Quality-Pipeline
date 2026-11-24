import json
from pathlib import Path

import pandas as pd

from src.storage.database import (
    get_connection,
    load_data_to_database,
    list_tables
)

from src.analytics.queries import (
    get_customer_summary,
    get_transaction_summary,
    get_customer_transaction_summary,
    get_rejected_customers,
    get_quality_metrics,
    get_unmatched_transactions
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SILVER_DIR = PROJECT_ROOT / "data" / "silver"

QUARANTINE_DIR = PROJECT_ROOT / "data" / "quarantine"

REPORT_DIR = (
    PROJECT_ROOT / "data" / "gold" / "reports"
)

TRANSACTIONS_FILE = (
    PROJECT_ROOT / "data" / "raw" / "transactions.csv"
)


def get_latest_file(directory, pattern):

    files = list(directory.glob(pattern))

    if not files:

        raise FileNotFoundError(
            f"No matching files found in {directory}"
        )

    return max(
        files,
        key=lambda path: path.stat().st_mtime_ns
    )


def main():

    print("Starting DuckDB analytics pipeline...")

    report_file = get_latest_file(
        REPORT_DIR,
        "integrated_report_*.json"
    )

    with report_file.open(
        "r",
        encoding="utf-8"
    ) as file:

        report = json.load(file)

    batch_id = report["batch_id"]

    customers_file = (
        SILVER_DIR / f"customers_{batch_id}.parquet"
    )

    rejected_file = (
        QUARANTINE_DIR / f"customers_{batch_id}.parquet"
    )

    customers_df = pd.read_parquet(customers_file)

    rejected_df = pd.read_parquet(rejected_file)

    transactions_df = pd.read_csv(
        TRANSACTIONS_FILE,
        dtype=str,
        keep_default_na=False
    )

    transactions_df["amount"] = pd.to_numeric(
        transactions_df["amount"],
        errors="raise"
    )

    metrics = report["customer_data_quality"]["metrics"]

    metrics_df = pd.DataFrame([{
        "batch_id": batch_id,
        **metrics,
        "quality_status": report[
            "customer_data_quality"
        ]["quality_status"]
    }])

    connection = get_connection()

    try:

        load_data_to_database(
            connection,
            customers_df,
            transactions_df,
            rejected_df,
            metrics_df
        )

        print("\nDATABASE TABLES")
        print(list_tables(connection).to_string(index=False))

        print("\nCUSTOMER SUMMARY")
        print(get_customer_summary(
            connection
        ).to_string(index=False))

        print("\nTRANSACTION SUMMARY")
        print(get_transaction_summary(
            connection
        ).to_string(index=False))

        print("\nCUSTOMER TRANSACTION SUMMARY")
        print(get_customer_transaction_summary(
            connection
        ).to_string(index=False))

        print("\nREJECTED CUSTOMERS")
        print(get_rejected_customers(
            connection
        ).to_string(index=False))

        print("\nDATA QUALITY METRICS")
        print(get_quality_metrics(
            connection
        ).to_string(index=False))

        print("\nUNMATCHED TRANSACTIONS")
        print(get_unmatched_transactions(
            connection
        ).to_string(index=False))

    finally:

        connection.close()

    print("\nDuckDB analytics completed successfully!")


if __name__ == "__main__":

    main()