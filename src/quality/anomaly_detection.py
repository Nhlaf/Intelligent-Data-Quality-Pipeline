import pandas as pd

from sklearn.ensemble import IsolationForest


def detect_transaction_anomalies(
    df: pd.DataFrame,
    contamination: float = 0.05
) -> pd.DataFrame:
    """
    Detect unusual transaction amounts using Isolation Forest.

    Returns a DataFrame with anomaly predictions
    and anomaly scores.
    """

    if "amount" not in df.columns:
        raise ValueError("Missing required column: amount")

    if df.empty:
        raise ValueError("Cannot detect anomalies in empty data")

    if not 0 < contamination <= 0.5:
        raise ValueError(
            "contamination must be greater than 0 and at most 0.5"
        )

    result = df.copy()

    result["amount"] = pd.to_numeric(
        result["amount"],
        errors="coerce"
    )

    if result["amount"].isna().any():
        raise ValueError(
            "Transaction amounts must be valid numbers"
        )

    if (result["amount"] < 0).any():
        raise ValueError(
            "Transaction amounts cannot be negative"
        )

    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=42
    )

    features = result[["amount"]]

    result["anomaly_prediction"] = model.fit_predict(
        features
    )

    result["anomaly_score"] = model.decision_function(
        features
    )

    result["anomaly_status"] = result[
        "anomaly_prediction"
    ].map({
        1: "Normal",
        -1: "Anomaly"
    })

    return result