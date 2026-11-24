from uuid import UUID

from fastapi import FastAPI, HTTPException

from api.schemas import (
    HealthResponse,
    CustomerQualityResponse,
    AnomalyResponse,
    IntegratedReportResponse,
    AIAnalysisResponse,
    ReportSummary
)

from api.services import (
    list_report_files,
    get_latest_report,
    get_report_by_batch_id,
    get_customer_quality,
    get_transaction_anomalies,
    get_ai_analysis
)


app = FastAPI(
    title="Intelligent Data Quality API",
    description=(
        "REST API for banking data quality monitoring, "
        "machine learning anomaly detection and AI analysis."
    ),
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "application": "Intelligent Data Quality Pipeline",
        "version": "1.0.0",
        "documentation": "/docs"
    }


@app.get(
    "/health",
    response_model=HealthResponse
)
def health_check():
    return {
        "status": "healthy",
        "service": "data-quality-api"
    }


@app.get(
    "/api/v1/reports",
    response_model=list[ReportSummary]
)
def list_reports():

    reports = list_report_files()

    return [
        {
            "batch_id": path.stem.removeprefix(
                "integrated_report_"
            ),
            "filename": path.name
        }
        for path in reports
    ]


@app.get(
    "/api/v1/reports/latest",
    response_model=IntegratedReportResponse
)
def latest_report():

    try:
        return get_latest_report()

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        ) from error


@app.get(
    "/api/v1/reports/{batch_id}",
    response_model=IntegratedReportResponse
)
def report_by_batch_id(batch_id: UUID):

    try:
        return get_report_by_batch_id(batch_id)

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        ) from error


@app.get(
    "/api/v1/quality",
    response_model=CustomerQualityResponse
)
def customer_quality():

    try:
        return get_customer_quality()

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        ) from error


@app.get(
    "/api/v1/anomalies",
    response_model=AnomalyResponse
)
def transaction_anomalies():

    try:
        return get_transaction_anomalies()

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        ) from error


@app.get(
    "/api/v1/ai-analysis",
    response_model=AIAnalysisResponse
)
def ai_analysis():

    try:
        return get_ai_analysis()

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        ) from error