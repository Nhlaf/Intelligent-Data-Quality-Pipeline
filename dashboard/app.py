import json
from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REPORT_DIR = PROJECT_ROOT / "data" / "gold" / "reports"

AI_ANALYSIS_DIR = (
    PROJECT_ROOT / "data" / "gold" / "ai_analysis"
)


st.set_page_config(
    page_title="Intelligent Data Quality Dashboard",
    page_icon="📊",
    layout="wide"
)


def get_report_files():
    return sorted(
        REPORT_DIR.glob("integrated_report_*.json"),
        key=lambda path: path.stat().st_mtime_ns,
        reverse=True
    )


def load_report(report_path):
    with report_path.open(
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def load_ai_analysis(batch_id):
    analysis_file = (
        AI_ANALYSIS_DIR / f"ai_analysis_{batch_id}.md"
    )

    if not analysis_file.exists():
        return None

    return analysis_file.read_text(
        encoding="utf-8"
    )


def main():

    st.title("Intelligent Data Quality Dashboard")

    st.caption(
        "Banking Data Quality Monitoring and AI Analysis"
    )

    # SIDEBAR

    st.sidebar.header("Dashboard Controls")

    report_files = get_report_files()

    if not report_files:
        st.warning(
            "No integrated reports found. "
            "Run the integrated quality pipeline first."
        )
        st.stop()

    selected_report = st.sidebar.selectbox(
        "Select a report",
        options=report_files,
        format_func=lambda path: path.name
    )

    if st.sidebar.button("Refresh Dashboard"):
        st.rerun()

    report = load_report(selected_report)

    batch_id = report["batch_id"]

    st.sidebar.subheader("Report Information")

    st.sidebar.write("Batch ID:")
    st.sidebar.code(batch_id)

    st.sidebar.write(
        f"Generated at: {report['generated_at']}"
    )

    customer_quality = report["customer_data_quality"]

    metrics = customer_quality["metrics"]

    rules = customer_quality["quality_rules"]

    quality_status = customer_quality["quality_status"]

    anomalies = report["transaction_anomaly_detection"]

    # DASHBOARD TABS

    overview_tab, quality_tab, anomaly_tab, ai_tab = st.tabs([
        "Overview",
        "Data Quality",
        "Anomaly Detection",
        "AI Analysis"
    ])

    # OVERVIEW TAB

    with overview_tab:

        st.subheader("Customer Data Quality Overview")

        if quality_status == "PASS":
            st.success("Overall Customer Quality Status: PASS")
        else:
            st.error("Overall Customer Quality Status: FAIL")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Records",
            metrics["total_records"]
        )

        col2.metric(
            "Valid Records",
            metrics["valid_records"]
        )

        col3.metric(
            "Rejected Records",
            metrics["invalid_records"]
        )

        col4.metric(
            "Duplicate Records",
            metrics["duplicate_count"]
        )

        st.divider()

        col5, col6, col7 = st.columns(3)

        col5.metric(
            "Validation Success",
            f"{metrics['validation_success_rate']}%"
        )

        col6.metric(
            "Completeness",
            f"{metrics['completeness_rate']}%"
        )

        col7.metric(
            "Rejection Rate",
            f"{metrics['rejection_rate']}%"
        )

        st.subheader("Customer Validation Results")

        chart_data = pd.DataFrame({
            "Status": ["Valid", "Invalid"],
            "Records": [
                metrics["valid_records"],
                metrics["invalid_records"]
            ]
        })

        st.bar_chart(
            chart_data,
            x="Status",
            y="Records"
        )

        st.divider()

        st.subheader("Transaction Monitoring Summary")

        col8, col9, col10 = st.columns(3)

        col8.metric(
            "Total Transactions",
            anomalies["total_transactions"]
        )

        col9.metric(
            "Anomalies Detected",
            anomalies["anomaly_count"]
        )

        col10.metric(
            "Anomaly Rate",
            f"{anomalies['anomaly_rate']}%"
        )

    # DATA QUALITY TAB

    with quality_tab:

        st.subheader("Data Quality Rule Evaluation")

        validation_passed = (
            metrics["validation_success_rate"]
            >= rules["validation_success_threshold"]
        )

        completeness_passed = (
            metrics["completeness_rate"]
            >= rules["completeness_threshold"]
        )

        duplicates_passed = (
            metrics["duplicate_count"]
            <= rules["maximum_duplicate_count"]
        )

        quality_table = pd.DataFrame([
            {
                "Quality Rule": "Validation Success",
                "Actual": (
                    f"{metrics['validation_success_rate']}%"
                ),
                "Threshold": (
                    f">= {rules['validation_success_threshold']}%"
                ),
                "Status": (
                    "PASS" if validation_passed else "FAIL"
                )
            },
            {
                "Quality Rule": "Completeness",
                "Actual": (
                    f"{metrics['completeness_rate']}%"
                ),
                "Threshold": (
                    f">= {rules['completeness_threshold']}%"
                ),
                "Status": (
                    "PASS" if completeness_passed else "FAIL"
                )
            },
            {
                "Quality Rule": "Duplicate Count",
                "Actual": str(metrics["duplicate_count"]),
                "Threshold": (
                    f"<= {rules['maximum_duplicate_count']}"
                ),
                "Status": (
                    "PASS" if duplicates_passed else "FAIL"
                )
            }
        ])

        st.dataframe(
            quality_table,
            hide_index=True,
            use_container_width="stretch"
        )

        st.subheader("Validation Success Rate")

        st.progress(
            metrics["validation_success_rate"] / 100
        )

        st.write(
            f"Actual: {metrics['validation_success_rate']}% | "
            f"Target: {rules['validation_success_threshold']}%"
        )

        st.subheader("Completeness Rate")

        st.progress(
            metrics["completeness_rate"] / 100
        )

        st.write(
            f"Actual: {metrics['completeness_rate']}% | "
            f"Target: {rules['completeness_threshold']}%"
        )

        st.subheader("Raw Quality Metrics")

        st.json(metrics)

    # ANOMALY DETECTION TAB

    with anomaly_tab:

        st.subheader("AI Transaction Anomaly Detection")

        st.caption(
            "Machine learning model: Isolation Forest"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Transactions",
            anomalies["total_transactions"]
        )

        col2.metric(
            "Flagged Transactions",
            anomalies["anomaly_count"]
        )

        col3.metric(
            "Anomaly Rate",
            f"{anomalies['anomaly_rate']}%"
        )

        normal_count = (
            anomalies["total_transactions"]
            - anomalies["anomaly_count"]
        )

        anomaly_chart = pd.DataFrame({
            "Classification": ["Normal", "Anomaly"],
            "Transactions": [
                normal_count,
                anomalies["anomaly_count"]
            ]
        })

        st.bar_chart(
            anomaly_chart,
            x="Classification",
            y="Transactions"
        )

        st.subheader("Flagged Transactions")

        flagged = anomalies["flagged_transactions"]

        if flagged:

            flagged_df = pd.DataFrame(flagged)

            st.dataframe(
                flagged_df,
                hide_index=True,
                use_container_width="stretch"
            )

            st.warning(
                "Flagged transactions require investigation. "
                "An anomaly does not prove fraud."
            )

            st.download_button(
                label="Download Flagged Transactions",
                data=flagged_df.to_csv(index=False),
                file_name="flagged_transactions.csv",
                mime="text/csv"
            )

        else:
            st.success("No transaction anomalies detected.")

    # AI ANALYSIS TAB

    with ai_tab:

        st.subheader("AI Data Quality Analyst")

        st.caption(
            "AI-generated findings and recommendations"
        )

        analysis = load_ai_analysis(batch_id)

        if analysis:

            st.markdown(analysis)

            st.download_button(
                label="Download AI Analysis",
                data=analysis,
                file_name=f"ai_analysis_{batch_id}.md",
                mime="text/markdown"
            )

            st.info(
                "AI recommendations should be reviewed "
                "by a human before corrective action."
            )

        else:
            st.warning(
                "No AI analysis found for this batch. "
                "Run the AI Agent first."
            )

    # DOWNLOAD INTEGRATED REPORT

    st.sidebar.divider()

    st.sidebar.download_button(
        label="Download JSON Report",
        data=json.dumps(report, indent=4),
        file_name=selected_report.name,
        mime="application/json"
    )


if __name__ == "__main__":
    main()