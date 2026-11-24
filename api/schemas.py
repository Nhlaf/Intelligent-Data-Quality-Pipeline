from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str


class QualityMetrics(BaseModel):
    total_records: int
    valid_records: int
    invalid_records: int
    validation_success_rate: float
    rejection_rate: float
    completeness_rate: float
    duplicate_count: int


class QualityRules(BaseModel):
    validation_success_threshold: float
    completeness_threshold: float
    maximum_duplicate_count: int


class CustomerQualityResponse(BaseModel):
    metrics: QualityMetrics
    quality_rules: QualityRules
    quality_status: str


class FlaggedTransaction(BaseModel):
    transaction_id: str
    customer_id: str
    amount: float
    anomaly_score: float


class AnomalyResponse(BaseModel):
    total_transactions: int
    anomaly_count: int
    anomaly_rate: float
    flagged_transactions: list[FlaggedTransaction]


class IntegratedReportResponse(BaseModel):
    report_type: str
    batch_id: str
    generated_at: str
    customer_data_quality: CustomerQualityResponse
    transaction_anomaly_detection: AnomalyResponse


class AIAnalysisResponse(BaseModel):
    batch_id: str
    analysis: str


class ReportSummary(BaseModel):
    batch_id: str
    filename: str