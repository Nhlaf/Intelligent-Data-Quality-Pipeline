from pathlib import Path

import duckdb
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = (
    PROJECT_ROOT / "data" / "gold" / "data_quality.duckdb"
)


def get_connection(database_path=DATABASE_PATH):

    database_path = Path(database_path)

    database_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    return duckdb.connect(str(database_path))


def load_data_to_database(
    connection,
    customers_df: pd.DataFrame,
    transactions_df: pd.DataFrame,
    rejected_df: pd.DataFrame,
    metrics_df: pd.DataFrame
):

    connection.register(
        "customers_source",
        customers_df
    )

    connection.register(
        "transactions_source",
        transactions_df
    )

    connection.register(
        "rejected_source",
        rejected_df
    )

    connection.register(
        "metrics_source",
        metrics_df
    )

    connection.execute("BEGIN TRANSACTION")

    try:

        connection.execute("""
            CREATE OR REPLACE TABLE customers AS
            SELECT * FROM customers_source
        """)

        connection.execute("""
            CREATE OR REPLACE TABLE transactions AS
            SELECT * FROM transactions_source
        """)

        connection.execute("""
            CREATE OR REPLACE TABLE rejected_customers AS
            SELECT * FROM rejected_source
        """)

        connection.execute("""
            CREATE OR REPLACE TABLE quality_metrics AS
            SELECT * FROM metrics_source
        """)

        connection.execute("COMMIT")

    except Exception:

        connection.execute("ROLLBACK")
        raise

    finally:

        connection.unregister("customers_source")
        connection.unregister("transactions_source")
        connection.unregister("rejected_source")
        connection.unregister("metrics_source")


def list_tables(connection):

    return connection.execute(
        "SHOW TABLES"
    ).fetchdf()