import json

from pathlib import Path

from src.orchestration.pipeline import run_pipeline
from src.utils.logger import setup_logger


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PIPELINE_REPORT_DIR = (
    PROJECT_ROOT
    / "data"
    / "gold"
    / "pipeline_runs"
)


def main():

    logger = setup_logger()

    try:

        result = run_pipeline()

        PIPELINE_REPORT_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        report_path = (
            PIPELINE_REPORT_DIR
            / f"pipeline_run_{result['pipeline_id']}.json"
        )

        with report_path.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                result,
                file,
                indent=4
            )

        logger.info(
            "Pipeline report saved: %s",
            report_path
        )

        print("\nPIPELINE EXECUTION SUMMARY")
        print("--------------------------")

        print(f"Pipeline ID: {result['pipeline_id']}")
        print(f"Status: {result['pipeline_status']}")
        print(f"Total stages: {result['total_stages']}")
        print(f"Executed stages: {result['executed_stages']}")
        print(f"Successful stages: {result['successful_stages']}")
        print(f"Failed stages: {result['failed_stages']}")
        print(f"Duration: {result['duration_seconds']} seconds")

        print("\nSTAGE RESULTS")

        for stage in result["stages"]:

            print(
                f"{stage['stage']}: "
                f"{stage['status']} "
                f"({stage['duration_seconds']}s)"
            )

            if stage["error_message"]:

                print(
                    f"Error: {stage['error_message']}"
                )

        if result["pipeline_status"] == "FAILED":

            raise SystemExit(1)

    except Exception as exc:

        logger.critical(
            "Pipeline execution failed: %s",
            type(exc).__name__
        )

        raise SystemExit(1) from exc


if __name__ == "__main__":

    main()