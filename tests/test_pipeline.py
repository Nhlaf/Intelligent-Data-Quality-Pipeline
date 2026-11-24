from unittest.mock import patch

from src.orchestration.pipeline import (
    execute_stage,
    run_pipeline,
    PIPELINE_STAGES
)


def test_pipeline_stage_configuration():

    assert len(PIPELINE_STAGES) == 6

    assert PIPELINE_STAGES[0][1] == (
        "scripts.run_ingestion"
    )

    assert PIPELINE_STAGES[-1][1] == (
        "scripts.run_ai_agent"
    )


@patch("src.orchestration.pipeline.subprocess.run")
def test_successful_stage(mock_run):

    mock_run.return_value.returncode = 0

    result = execute_stage(
        "Test Stage",
        "scripts.test_stage"
    )

    assert result["status"] == "SUCCESS"
    assert result["return_code"] == 0


@patch("src.orchestration.pipeline.subprocess.run")
def test_failed_stage(mock_run):

    mock_run.return_value.returncode = 1

    result = execute_stage(
        "Test Stage",
        "scripts.test_stage"
    )

    assert result["status"] == "FAILED"
    assert result["return_code"] == 1


@patch("src.orchestration.pipeline.subprocess.run")
def test_successful_pipeline(mock_run):

    mock_run.return_value.returncode = 0

    result = run_pipeline()

    assert result["pipeline_status"] == "SUCCESS"
    assert result["total_stages"] == 6
    assert result["executed_stages"] == 6
    assert result["successful_stages"] == 6
    assert result["failed_stages"] == 0


@patch("src.orchestration.pipeline.subprocess.run")
def test_pipeline_stops_on_failure(mock_run):

    mock_run.return_value.returncode = 1

    result = run_pipeline()

    assert result["pipeline_status"] == "FAILED"
    assert result["executed_stages"] == 1
    assert result["successful_stages"] == 0
    assert result["failed_stages"] == 1

    assert mock_run.call_count == 1


@patch("src.orchestration.pipeline.subprocess.run")
def test_pipeline_metadata(mock_run):

    mock_run.return_value.returncode = 0

    result = run_pipeline()

    assert "pipeline_id" in result
    assert "started_at" in result
    assert "completed_at" in result
    assert "duration_seconds" in result

    assert result["duration_seconds"] >= 0