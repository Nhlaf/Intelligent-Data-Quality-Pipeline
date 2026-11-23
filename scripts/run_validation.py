from pathlib import Path

import pandas as pd

from src.validation.validator import validate_customers


PROJECT_ROOT = Path(__file__).resolve().parents[1]

BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"
SILVER_DIR = PROJECT_ROOT / "data" / "silver"
QUARANTINE_DIR = PROJECT_ROOT / "data" / "quarantine"


def main():
    print("Starting customer data validation...")

    bronze_files = list(BRONZE_DIR.glob("customers_*.parquet"))

    if not bronze_files:
        raise FileNotFoundError("No Bronze files found")

    latest_file = max(
        bronze_files,
        key=lambda path: path.stat().st_mtime_ns
    )

    print(f"Reading: {latest_file.name}")

    df = pd.read_parquet(latest_file)

    valid_df, invalid_df = validate_customers(df)

    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

    batch_id = latest_file.stem.removeprefix("customers_")

    silver_path = SILVER_DIR / f"customers_{batch_id}.parquet"
    quarantine_path = (
        QUARANTINE_DIR / f"customers_{batch_id}.parquet"
    )

    valid_df.to_parquet(silver_path, index=False)
    invalid_df.to_parquet(quarantine_path, index=False)

    print(f"Total records: {len(df)}")
    print(f"Valid records: {len(valid_df)}")
    print(f"Invalid records: {len(invalid_df)}")

    print(f"Silver file saved: {silver_path}")
    print(f"Quarantine file saved: {quarantine_path}")

    print("Validation completed successfully!")


if __name__ == "__main__":
    main()