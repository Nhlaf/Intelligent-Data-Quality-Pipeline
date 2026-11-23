import json
from pathlib import Path

from src.ai_agent.data_quality_agent import (
    analyze_data_quality
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REPORT_DIR = (
    PROJECT_ROOT / "data" / "gold" / "reports"
)

OUTPUT_DIR = (
    PROJECT_ROOT / "data" / "gold" / "ai_analysis"
)


def main():
    print("Starting AI Data Quality Agent...")

    report_files = list(
        REPORT_DIR.glob("integrated_report_*.json")
    )

    if not report_files:
        raise FileNotFoundError(
            "No integrated reports found. "
            "Run the integrated pipeline first."
        )

    latest_report = max(
        report_files,
        key=lambda path: path.stat().st_mtime_ns
    )

    print(f"Reading: {latest_report.name}")

    with latest_report.open(
        "r",
        encoding="utf-8"
    ) as file:
        report = json.load(file)

    print("Sending quality summary to AI model...")

    analysis = analyze_data_quality(report)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    batch_id = report["batch_id"]

    output_file = (
        OUTPUT_DIR / f"ai_analysis_{batch_id}.md"
    )

    output_file.write_text(
        analysis,
        encoding="utf-8"
    )

    print("\nAI DATA QUALITY ANALYSIS")
    print("---------------------------")

    print(analysis)

    print(f"\nAnalysis saved: {output_file}")
    print("\nAI Agent completed successfully!")


if __name__ == "__main__":
    main()