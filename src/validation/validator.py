import pandas as pd
from pydantic import ValidationError

from src.validation.customer_schema import CustomerSchema


def validate_customers(df: pd.DataFrame):
    valid_records = []
    invalid_records = []

    required_columns = [
        "customer_id",
        "full_name",
        "email",
        "customer_status"
    ]

    required_metadata = [
        "batch_id",
        "ingestion_timestamp"
    ]

    expected_columns = required_columns + required_metadata

    missing_columns = [
        column for column in expected_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    seen_customer_ids = set()

    for _, row in df.iterrows():
        customer = row[required_columns].to_dict()
        customer_id = str(customer["customer_id"]).strip()

        try:
            validated = CustomerSchema.model_validate(customer)

            if customer_id in seen_customer_ids:
                raise ValueError(
                    f"Duplicate customer ID: {customer_id}"
                )

            seen_customer_ids.add(customer_id)

            valid_record = validated.model_dump()

            for column in required_metadata:
                valid_record[column] = row[column]

            valid_records.append(valid_record)

        except (ValidationError, ValueError) as error:
            invalid_record = row.to_dict()

            if isinstance(error, ValidationError):
                reason = "; ".join(
                    issue["msg"] for issue in error.errors()
                )
            else:
                reason = str(error)

            invalid_record["rejection_reason"] = reason

            invalid_records.append(invalid_record)

    valid_df = pd.DataFrame(
        valid_records,
        columns=expected_columns
    )

    invalid_df = pd.DataFrame(
        invalid_records,
        columns=list(df.columns) + ["rejection_reason"]
    )

    return valid_df, invalid_df