from pathlib import Path
import pandas as pd


def load_csv(file_path: str | Path) -> pd.DataFrame:
    """
    Read a CSV file and return a Pandas DataFrame.
    """

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    try:
        df = pd.read_csv(
            path,
            dtype=str,
            keep_default_na=False
        )
    except pd.errors.EmptyDataError as exc:
        raise ValueError(
            "CSV file is empty"
        ) from exc

    if df.empty:
        raise ValueError(
            "CSV contains no records"
        )

    return df