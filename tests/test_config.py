import json

import pytest

from src.quality.config import (
    evaluate_quality,
    load_quality_rules
)


def test_load_quality_rules(tmp_path):
    rules = {
        "validation_success_threshold": 95.0,
        "completeness_threshold": 98.0,
        "maximum_duplicate_count": 0
    }

    config_file = tmp_path / "quality_rules.json"
    config_file.write_text(json.dumps(rules))

    loaded = load_quality_rules(config_file)

    assert loaded == rules


def test_quality_pass():
    metrics = {
        "validation_success_rate": 99.0,
        "completeness_rate": 100.0,
        "duplicate_count": 0
    }

    rules = {
        "validation_success_threshold": 95.0,
        "completeness_threshold": 98.0,
        "maximum_duplicate_count": 0
    }

    assert evaluate_quality(metrics, rules) == "PASS"


def test_quality_fail():
    metrics = {
        "validation_success_rate": 80.0,
        "completeness_rate": 100.0,
        "duplicate_count": 0
    }

    rules = {
        "validation_success_threshold": 95.0,
        "completeness_threshold": 98.0,
        "maximum_duplicate_count": 0
    }

    assert evaluate_quality(metrics, rules) == "FAIL"


def test_missing_quality_rule(tmp_path):
    config_file = tmp_path / "quality_rules.json"

    config_file.write_text(
        json.dumps({"validation_success_threshold": 95.0})
    )

    with pytest.raises(ValueError, match="Missing quality rule"):
        load_quality_rules(config_file)