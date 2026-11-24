import subprocess
import sys
import time

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from src.utils.logger import setup_logger


PROJECT_ROOT = Path(__file__).resolve().parents[2]

STAGE_TIMEOUT = 120


PIPELINE_STAGES = [
    ("Data Ingestion", "scripts.run_ingestion"),
    ("Data Validation", "scripts.run_validation"),
    ("Data Quality Assessment", "scripts.run_quality"),
    ("Integrated Quality Report", "scripts.run_integrated_quality"),
    ("DuckDB Analytics", "scripts.run_analytics"),
    ("AI Data Quality Agent", "scripts.run_ai_agent")
]


def execute_stage(
    stage_name: str,
    module_name: str
) -> dict:

    logger = setup_logger()

    logger.info(
        "Starting stage: %s",
        stage_name
    )

    start_time = time.perf_counter()

    status = "FAILED"
    return_code = None
    error_message = None

    try:

        result = subprocess.run(
            [sys.executable, "-m", module_name],
            cwd=PROJECT_ROOT,
            check=False,
            timeout=STAGE_TIMEOUT
        )

        return_code = result.returncode

        if return_code == 0:

            status = "SUCCESS"

        else:

            error_message = (
                f"Stage exited with code {return_code}"
            )

            logger.error(
                "%s: %s",
                stage_name,
                error_message
            )

    except subprocess.TimeoutExpired:

        error_message = (
            f"Stage exceeded the "
            f"{STAGE_TIMEOUT}-second timeout"
        )

        logger.error(
            "%s: %s",
            stage_name,
            error_message
        )

    except Exception as exc:

        error_message = (
            f"Unexpected execution error: "
            f"{type(exc).__name__}"
        )

        logger.error(
            "%s: %s",
            stage_name,
            error_message
        )

    duration = round(
        time.perf_counter() - start_time,
        2
    )

    logger.info(
        "Stage: %s | Status: %s | Duration: %ss",
        stage_name,
        status,
        duration
    )

    return {
        "stage": stage_name,
        "module": module_name,
        "status": status,
        "duration_seconds": duration,
        "return_code": return_code,
        "error_message": error_message
    }


def run_pipeline(stages=None) -> dict:

    logger = setup_logger()

    if stages is None:
        stages = PIPELINE_STAGES

    pipeline_id = str(uuid4())

    started_at = datetime.now(
        timezone.utc
    ).isoformat()

    start_time = time.perf_counter()

    results = []

    pipeline_status = "SUCCESS"

    logger.info(
        "Pipeline started | ID: %s",
        pipeline_id
    )

    for stage_name, module_name in stages:

        result = execute_stage(
            stage_name,
            module_name
        )

        results.append(result)

        if result["status"] == "FAILED":

            pipeline_status = "FAILED"

            logger.error(
                "Pipeline %s stopped at stage: %s",
                pipeline_id,
                stage_name
            )

            break

    duration = round(
        time.perf_counter() - start_time,
        2
    )

    logger.info(
        "Pipeline completed | ID: %s | "
        "Status: %s | Duration: %ss",
        pipeline_id,
        pipeline_status,
        duration
    )

    return {
        "pipeline_id": pipeline_id,
        "started_at": started_at,
        "completed_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "pipeline_status": pipeline_status,
        "total_stages": len(stages),
        "executed_stages": len(results),
        "successful_stages": sum(
            result["status"] == "SUCCESS"
            for result in results
        ),
        "failed_stages": sum(
            result["status"] == "FAILED"
            for result in results
        ),
        "duration_seconds": duration,
        "stages": results
    }