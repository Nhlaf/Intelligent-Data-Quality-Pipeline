from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4

import pandas as pd


def save_to_bronze(
    df: pd.DataFrame,
    output_dir: str | Path
) -> Path:
    """
    Save raw ingested data to the Bronze layer.
    """

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    batch_id = str(uuid4())
    ingestion_time = datetime.now(timezone.utc)

    bronze_df = df.copy()

    bronze_df["batch_id"] = batch_id
    bronze_df["ingestion_timestamp"] = ingestion_time.isoformat()

    file_path = output_path / f"customers_{batch_id}.parquet"

    bronze_df.to_parquet(
        file_path,
        engine="pyarrow",
        index=False
    )

    return file_path