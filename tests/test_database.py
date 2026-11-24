import pandas as pd
import pytest

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


@pytest.fixture
def database(tmp_path):

    connection = get_connection(
        tmp_path / "test.duckdb"
    )

    customers = pd.DataFrame([
        {
            "customer_id": "C001",
            "full_name": "Test Customer",
            "customer_status": "Active"
        }
    ])

    transactions = pd.DataFrame([
        {
            "transaction_id": "T001",
            "customer_id": "C001",
            "amount": 500.0
        },
        {
            "transaction_id": "T002",
            "customer_id": "C999",
            "amount": 1000.0
        }
    ])

    rejected = pd.DataFrame([
        {
            "customer_id": "C002",
            "rejection_reason": "Invalid status"
        }
    ])

    metrics = pd.DataFrame([
        {
            "total_records": 2,
            "valid_records": 1,
            "invalid_records": 1,
            "quality_status": "FAIL"
        }
    ])

    load_data_to_database(
        connection,
        customers,
        transactions,
        rejected,
        metrics
    )

    try:

        yield connection

    finally:

        connection.close()


def test_database_tables(database):

    tables = list_tables(database)

    assert set(tables["name"]) == {
        "customers",
        "transactions",
        "rejected_customers",
        "quality_metrics"
    }


def test_customer_summary(database):

    result = get_customer_summary(database)

    assert result.iloc[0]["customer_status"] == "Active"

    assert result.iloc[0]["total_customers"] == 1


def test_transaction_summary(database):

    result = get_transaction_summary(database)

    assert result.iloc[0]["total_transactions"] == 2

    assert result.iloc[0]["total_amount"] == 1500.0


def test_customer_transaction_summary(database):

    result = get_customer_transaction_summary(database)

    assert result.iloc[0]["transaction_count"] == 1

    assert result.iloc[0]["total_transaction_amount"] == 500.0


def test_rejected_customers(database):

    result = get_rejected_customers(database)

    assert len(result) == 1

    assert result.iloc[0]["customer_id"] == "C002"


def test_quality_metrics(database):

    result = get_quality_metrics(database)

    assert result.iloc[0]["quality_status"] == "FAIL"


def test_unmatched_transactions(database):

    result = get_unmatched_transactions(database)

    assert len(result) == 1

    assert result.iloc[0]["customer_id"] == "C999"