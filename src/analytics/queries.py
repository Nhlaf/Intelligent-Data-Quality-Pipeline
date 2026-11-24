def get_customer_summary(connection):

    return connection.execute("""
        SELECT
            customer_status,
            COUNT(*) AS total_customers
        FROM customers
        GROUP BY customer_status
        ORDER BY total_customers DESC
    """).fetchdf()


def get_transaction_summary(connection):

    return connection.execute("""
        SELECT
            COUNT(*) AS total_transactions,
            ROUND(SUM(amount), 2) AS total_amount,
            ROUND(AVG(amount), 2) AS average_amount,
            MIN(amount) AS minimum_amount,
            MAX(amount) AS maximum_amount
        FROM transactions
    """).fetchdf()


def get_customer_transaction_summary(connection):

    return connection.execute("""
        SELECT
            c.customer_id,
            c.full_name,
            COUNT(t.transaction_id) AS transaction_count,
            COALESCE(
                ROUND(SUM(t.amount), 2),
                0
            ) AS total_transaction_amount
        FROM customers c
        LEFT JOIN transactions t
            ON c.customer_id = t.customer_id
        GROUP BY
            c.customer_id,
            c.full_name
        ORDER BY total_transaction_amount DESC
    """).fetchdf()


def get_rejected_customers(connection):

    return connection.execute("""
        SELECT *
        FROM rejected_customers
    """).fetchdf()


def get_quality_metrics(connection):

    return connection.execute("""
        SELECT *
        FROM quality_metrics
    """).fetchdf()


def get_unmatched_transactions(connection):

    return connection.execute("""
        SELECT t.*
        FROM transactions t
        LEFT JOIN customers c
            ON t.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
    """).fetchdf()