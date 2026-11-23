from pathlib import Path

from src.ingestion.csv_ingestion import load_csv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CUSTOMER_FILE = (
    PROJECT_ROOT / "data" / "raw" / "customers.csv"
)


def main():
    print("Starting customer data ingestion...")

    customers = load_csv(CUSTOMER_FILE)

    print(f"Total records: {len(customers)}")

    print("\nCustomer Data:")
    print(customers.to_string(index=False))

    print("\nIngestion completed successfully!")


if __name__ == "__main__":
    main()