from pathlib import Path

from src.ingestion.csv_ingestion import load_csv
from src.storage.bronze import save_to_bronze


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CUSTOMER_FILE = PROJECT_ROOT / "data" / "raw" / "customers.csv"

BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"


def main():
    print("Starting customer data ingestion...")

    customers = load_csv(CUSTOMER_FILE)

    print(f"Total records: {len(customers)}")

    bronze_file = save_to_bronze(
        customers,
        BRONZE_DIR
    )

    print(f"Bronze file saved: {bronze_file}")
    print("Ingestion completed successfully!")


if __name__ == "__main__":
    main()