import pandas as pd


def calculate_quality_metrics(
    bronze_df: pd.DataFrame,
    valid_df: pd.DataFrame,
    invalid_df: pd.DataFrame
) -> dict:

    total_records = len(bronze_df)
    valid_records = len(valid_df)
    invalid_records = len(invalid_df)

    if total_records == 0:
        raise ValueError("Cannot calculate metrics for empty data")

    required_columns = [
        "customer_id",
        "full_name",
        "email",
        "customer_status"
    ]

    # Count missing values and empty strings
    data = bronze_df[required_columns].fillna("")

    missing_cells = (
        data.astype(str)
        .apply(lambda col: col.str.strip().eq(""))
        .sum()
        .sum()
    )

    total_cells = total_records * len(required_columns)

    completeness_rate = (
        (total_cells - missing_cells) / total_cells
    ) * 100

    duplicate_count = bronze_df["customer_id"].duplicated(
        keep="first"
    ).sum()

    return {
        "total_records": total_records,
        "valid_records": valid_records,
        "invalid_records": invalid_records,
        "validation_success_rate": round(
            valid_records / total_records * 100, 2
        ),
        "rejection_rate": round(
            invalid_records / total_records * 100, 2
        ),
        "completeness_rate": round(
            completeness_rate, 2
        ),
        "duplicate_count": int(duplicate_count)
    }