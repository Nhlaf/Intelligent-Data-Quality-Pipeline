import logging
import subprocess

from uuid import uuid4
from unittest.mock import patch

import pytest

from src.utils.logger import setup_logger

from src.orchestration.pipeline import (
    execute_stage,
    run_pipeline
)


@pytest.fixture
def test_logger(tmp_path):

    logger = setup_logger(
        name=f"test_logger_{uuid4()}",
        log_dir=tmp_path
    )

    yield logger

    for handler in logger.handlers[:]:

        handler.close()

        logger.removeHandler(handler)


def test_logger_created(test_logger):

    assert isinstance(
        test_logger,
        logging.Logger
    )


def test_logger_level(test_logger):

    assert test_logger.level == logging.INFO


def test_log_file_created(test_logger, tmp_path):

    test_logger.info("Test pipeline message")

    log_file = tmp_path / "pipeline.log"

    assert log_file.exists()

    assert "Test pipeline message" in (
        log_file.read_text(encoding="utf-8")
    )


def test_no_duplicate_handlers(test_logger, tmp_path):

    initial_count = len(test_logger.handlers)

    same_logger = setup_logger(
        name=test_logger.name,
        log_dir=tmp_path
    )

    assert len(same_logger.handlers) == initial_count


@patch("src.orchestration.pipeline.subprocess.run")
def test_stage_timeout(mock_run):

    mock_run.side_effect = subprocess.TimeoutExpired(
        cmd="test_command",
        timeout=120
    )

    result = execute_stage(
        "Timeout Stage",
        "scripts.test_stage"
    )

    assert result["status"] == "FAILED"

    assert "timeout" in result["error_message"]

    assert result["return_code"] is None


@patch("src.orchestration.pipeline.subprocess.run")
def test_unexpected_stage_error(mock_run):

    mock_run.side_effect = RuntimeError(
        "Unexpected error"
    )

    result = execute_stage(
        "Error Stage",
        "scripts.test_stage"
    )

    assert result["status"] == "FAILED"

    assert "RuntimeError" in result["error_message"]


@patch("src.orchestration.pipeline.subprocess.run")
def test_successful_stage_has_no_error(mock_run):

    mock_run.return_value.returncode = 0

    result = execute_stage(
        "Successful Stage",
        "scripts.test_stage"
    )

    assert result["status"] == "SUCCESS"

    assert result["error_message"] is None


@patch("src.orchestration.pipeline.subprocess.run")
def test_pipeline_stops_after_timeout(mock_run):

    mock_run.side_effect = subprocess.TimeoutExpired(
        cmd="test_command",
        timeout=120
    )

    result = run_pipeline()

    assert result["pipeline_status"] == "FAILED"

    assert result["executed_stages"] == 1

    assert result["failed_stages"] == 1

    assert mock_run.call_count == 1