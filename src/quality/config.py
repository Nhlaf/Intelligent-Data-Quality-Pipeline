import json
from pathlib import Path


def load_quality_rules(config_path: str | Path) -> dict:
    path = Path(config_path)

    with path.open("r", encoding="utf-8") as file:
        rules = json.load(file)

    required_rules = [
        "validation_success_threshold",
        "completeness_threshold",
        "maximum_duplicate_count"
    ]

    for rule in required_rules:
        if rule not in rules:
            raise ValueError(f"Missing quality rule: {rule}")

    for rule in required_rules[:2]:
        value = rules[rule]

        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not 0 <= value <= 100
        ):
            raise ValueError(f"Invalid threshold: {rule}")

    count = rules["maximum_duplicate_count"]

    if type(count) is not int or count < 0:
        raise ValueError("Invalid maximum_duplicate_count")

    return rules


def evaluate_quality(metrics: dict, rules: dict) -> str:
    passed = (
        metrics["validation_success_rate"]
        >= rules["validation_success_threshold"]
        and metrics["completeness_rate"]
        >= rules["completeness_threshold"]
        and metrics["duplicate_count"]
        <= rules["maximum_duplicate_count"]
    )

    return "PASS" if passed else "FAIL"