"""Pydantic schemas for bulk operations (import, export, batch AI analysis)."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ────────────────────────────────────────────────────────────────────────────
# BULK RESUME IMPORT SCHEMAS
# ────────────────────────────────────────────────────────────────────────────

class ParsingResult(BaseModel):
    """Result of parsing a single resume file."""

    filename: str
    status: str = Field(..., description="success, error, duplicate")
    candidate_id: Optional[int] = None
    extracted_skills: Optional[List[str]] = None
    extracted_name: Optional[str] = None
    extracted_email: Optional[str] = None
    errors: Optional[List[str]] = None


class ImportBatchResult(BaseModel):
    """Result of bulk resume import operation."""

    batch_id: str
    total_files: int
    successfully_parsed: int
    failed: int
    candidates_created: int
    parsing_results: List[ParsingResult]
    imported_by: str = "system"
    created_at: datetime


class ExcelImportResult(BaseModel):
    """Result of Excel/CSV import."""

    batch_id: str
    total_rows: int
    successfully_imported: int
    skipped_duplicates: int
    validation_errors: int
    error_details: Optional[List[Dict[int, str]]] = None
    created_at: datetime


class PlacementImportResult(BaseModel):
    """Result of placement/associate import."""

    batch_id: str
    total_records: int
    created: int
    updated: int
    skipped: int
    error_details: Optional[List[Dict[str, Any]]] = None
    created_at: datetime


class RequirementImportResult(BaseModel):
    """Result of requirement import."""

    batch_id: str
    total_records: int
    created: int
    skipped: int
    error_details: Optional[List[Dict[str, Any]]] = None
    created_at: datetime


# ────────────────────────────────────────────────────────────────────────────
# BULK AI ANALYSIS SCHEMAS
# ────────────────────────────────────────────────────────────────────────────

class ScoredCandidate(BaseModel):
    """Single scored candidate result."""

    candidate_id: int
    candidate_name: str
    overall_score: float = Field(..., ge=0, le=100)
    skill_score: float
    experience_score: float
    education_score: float
    location_score: float
    rate_score: float
    availability_score: float
    culture_score: float


class BatchScoreResult(BaseModel):
    """Result of batch AI scoring."""

    batch_id: str
    requirement_id: int
    total_candidates: int
    scored_candidates: List[ScoredCandidate]
    avg_score: float
    score_distribution: Dict[str, int]
    processing_time_ms: int
    created_at: datetime


class ExtractedSkill(BaseModel):
    """Single extracted skill with proficiency."""

    skill: str
    proficiency: int = Field(..., ge=0, le=100)
    demand: str = Field(..., description="HIGH, MEDIUM, LOW")
    years_experience: float


class SkillExtractionResult(BaseModel):
    """Skill extraction result for a candidate."""

    candidate_id: int
    candidate_name: str
    extracted_skills: List[ExtractedSkill]
    total_skills: int
    skill_gaps_vs_market: Optional[List[str]] = None


class BatchSkillExtractionResult(BaseModel):
    """Result of batch skill extraction."""

    batch_id: str
    total_candidates: int
    candidates: List[SkillExtractionResult]
    created_at: datetime


class PlacementPrediction(BaseModel):
    """Placement probability prediction for a candidate."""

    candidate_id: int
    candidate_name: str
    placement_probability: float = Field(..., ge=0, le=100)
    time_to_fill_days: int
    risk_factors: List[str]


class BatchPlacementPredictionResult(BaseModel):
    """Result of batch placement prediction."""

    batch_id: str
    requirement_id: int
    total_candidates: int
    predictions: List[PlacementPrediction]
    created_at: datetime


class SkillMarketData(BaseModel):
    """Market analysis data for a single skill."""

    skill: str
    demand_level: str = Field(..., description="CRITICAL, HIGH, MEDIUM, LOW")
    avg_bill_rate: float
    avg_pay_rate: float
    supply_count: int
    demand_count: int
    competition_index: float = Field(..., ge=0, le=100)


class MarketAnalysisResult(BaseModel):
    """Market analysis result for multiple skills."""

    skills_analyzed: List[SkillMarketData]
    highest_demand_skill: str
    lowest_supply_skill: str
    created_at: datetime


# ────────────────────────────────────────────────────────────────────────────
# BULK AI ANALYSIS DASHBOARD SCHEMAS
# ────────────────────────────────────────────────────────────────────────────

class SkillDemandEntry(BaseModel):
    """Entry in skill demand heatmap."""

    skill: str
    demand_score: float = Field(..., ge=0, le=100)


class BulkAnalysisDashboard(BaseModel):
    """Comprehensive bulk AI analysis dashboard."""

    recent_batch_scores: List[BatchScoreResult]
    total_candidates_scored: int
    avg_platform_score: float
    skill_demand_heatmap: List[SkillDemandEntry]
    placement_success_rate: float = Field(..., ge=0, le=100)
    avg_time_to_fill_days: float
    ai_insights: List[str]
    generated_at: datetime


# ────────────────────────────────────────────────────────────────────────────
# EXPORT SCHEMAS
# ────────────────────────────────────────────────────────────────────────────

class ExportResult(BaseModel):
    """Result of bulk export operation."""

    export_id: str
    entity_type: str = Field(..., description="candidates, requirements, placements, submissions")
    format: str = Field(..., description="csv, json")
    filename: str
    record_count: int
    file_size_bytes: Optional[int] = None
    download_url: str
    expires_at: datetime
    generated_at: datetime


# ────────────────────────────────────────────────────────────────────────────
# IMPORT HISTORY & TEMPLATES
# ────────────────────────────────────────────────────────────────────────────

class ImportHistoryEntry(BaseModel):
    """Single import history record."""

    batch_id: str
    import_type: str
    total_records: int
    success_count: int
    error_count: int
    imported_by: str
    created_at: datetime


class ColumnDefinition(BaseModel):
    """Column definition for import template."""

    column_name: str
    required: bool
    description: str
    example: str


class TemplateInfo(BaseModel):
    """Import template information."""

    entity_type: str
    columns: List[ColumnDefinition]
    sample_data: Optional[List[Dict[str, Any]]] = None
    download_url: str
    created_at: datetime


# ────────────────────────────────────────────────────────────────────────────
# BACKGROUND JOB & IMPORT JOB SCHEMAS
# ────────────────────────────────────────────────────────────────────────────

class JobCreateResponse(BaseModel):
    """Response when creating a new import job."""

    job_id: int
    status: str = Field(..., description="QUEUED, PROCESSING, COMPLETED, COMPLETED_WITH_ERRORS, FAILED")
    status_url: str = Field(..., description="URL to check job status")
    message: str = Field(..., description="Human-readable message")


class FailureRecord(BaseModel):
    """A single failed import record."""

    row_number: int
    original_data: Dict[str, Any] = Field(..., description="All fields from the original row")
    errors: List[str] = Field(default_factory=list, description="List of validation errors")
    field_errors: Dict[str, str] = Field(default_factory=dict, description="Field-level error mapping")


class SkippedRecord(BaseModel):
    """A single skipped import record."""

    row_number: int
    original_data: Dict[str, Any]
    reason: str


class SuccessRecord(BaseModel):
    """Summary of a successfully imported record."""

    row_number: int
    data_summary: Dict[str, Any]
    created_id: Optional[int] = None


class ImportJobResponse(BaseModel):
    """Full details of an import job."""

    id: int
    user_id: int
    organization_id: Optional[int] = None
    job_type: str
    status: str
    total_records: int
    processed_records: int
    success_count: int
    failure_count: int
    skipped_count: int
    progress_percent: float
    file_name: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ImportJobListResponse(BaseModel):
    """Summary of an import job in a list."""

    id: int
    job_type: str
    status: str
    total_records: int
    success_count: int
    failure_count: int
    skipped_count: int
    progress_percent: float
    file_name: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class FailureDownloadResponse(BaseModel):
    """Response for downloading failure records as Excel."""

    download_url: str
    filename: str
    record_count: int
    columns: List[str]


class RetryResponse(BaseModel):
    """Response when retrying failed records."""

    new_job_id: int
    original_job_id: int
    records_to_retry: int
    status_url: str


class JobCompletionNotification(BaseModel):
    """Notification for job completion."""

    title: str
    message: str
    notification_type: str = Field(..., description="SUCCESS, WARNING, ALERT, INFO")
    action_url: str
