"""Dashboard and analytics response schemas."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class MetricValue(BaseModel):
    """A single metric value."""
    label: str
    value: Any
    unit: Optional[str] = None
    trend: Optional[float] = None  # percentage change
    previous_value: Optional[Any] = None


class OverviewMetrics(BaseModel):
    """Executive summary metrics."""
    total_active_requirements: int = Field(description="Total active job requirements")
    candidates_in_pipeline: int = Field(description="Total candidates in active pipeline")
    submissions_this_month: int = Field(description="Submissions made this calendar month")
    placements_this_month: int = Field(description="Placements completed this month")
    avg_time_to_fill_days: float = Field(description="Average days to fill a requirement")
    open_vs_filled_ratio: float = Field(description="Ratio of open to filled positions")
    total_candidates: int = Field(description="Total candidate pool")
    active_suppliers: int = Field(description="Number of active suppliers")


class PipelineStage(BaseModel):
    """Candidate count at each pipeline stage."""
    stage: str
    count: int
    percentage: float
    velocity_avg_days: Optional[float] = None


class PipelineMetrics(BaseModel):
    """Full pipeline view."""
    total_candidates: int
    stages: List[PipelineStage]
    bottleneck_stage: Optional[str] = None
    bottleneck_avg_days: Optional[float] = None


class RecruiterPerformance(BaseModel):
    """Single recruiter metrics."""
    recruiter_id: int
    recruiter_name: str
    email: str
    total_submissions: int
    total_placements: int
    placement_rate: float = Field(description="Percentage of submissions that became placements")
    avg_match_score: float = Field(description="Average match score of submissions")
    avg_time_to_fill_days: float
    active_requirements: int
    submissions_this_month: int


class RecruiterPerformanceMetrics(BaseModel):
    """All recruiters performance."""
    recruiters: List[RecruiterPerformance]
    total_recruiters: int
    top_performer_id: Optional[int] = None
    avg_placement_rate: float


class RequirementAnalytics(BaseModel):
    """Requirement analytics."""
    total_requirements: int
    active_requirements: int
    filled_requirements: int
    fill_rate: float = Field(description="Percentage of filled vs total requirements")
    avg_time_to_fill_days: float
    avg_time_to_fill_by_priority: Dict[str, float]
    top_skills_demanded: List[Dict[str, Any]]  # [{skill, count, avg_time_to_fill}]
    requirements_by_priority: Dict[str, int]


class SubmissionFunnelStage(BaseModel):
    """Single funnel stage."""
    stage: str
    count: int
    conversion_rate_from_previous: Optional[float] = None


class SubmissionFunnel(BaseModel):
    """Submission funnel metrics."""
    total_pipeline: int
    stages: List[SubmissionFunnelStage]
    overall_conversion_rate: float = Field(description="Total / final stage")


class OfferMetrics(BaseModel):
    """Offer metrics."""
    total_offers: int
    accepted_offers: int
    declined_offers: int
    negotiating_offers: int
    acceptance_rate: float = Field(description="Percentage of offers accepted")
    avg_negotiation_rounds: float
    backout_rate: float = Field(description="Percentage of accepted offers that backed out")
    avg_time_to_accept_days: float
    avg_offer_value: Optional[float] = None


class SupplierPerformance(BaseModel):
    """Single supplier performance."""
    supplier_id: int
    supplier_name: str
    tier: str
    total_placements: int
    total_submissions: int
    submission_to_placement_rate: float
    avg_match_quality: float
    this_month_placements: int
    rank: int


class SupplierLeaderboard(BaseModel):
    """Ranked suppliers."""
    suppliers: List[SupplierPerformance]
    total_suppliers: int
    period: str = "monthly"


class CandidateSourceBreakdown(BaseModel):
    """Candidates by source."""
    source: str
    count: int
    percentage: float
    placements: int
    placement_rate: float


class CandidateSourceMetrics(BaseModel):
    """All candidate sources."""
    total_candidates: int
    sources: List[CandidateSourceBreakdown]


class TimeSeriesDataPoint(BaseModel):
    """Single time series data point."""
    date: str  # YYYY-MM-DD format
    value: float
    label: Optional[str] = None


class TimeSeriesMetrics(BaseModel):
    """Historical trend data."""
    metric: str
    interval: str  # daily, weekly, monthly
    data_points: List[TimeSeriesDataPoint]
    start_date: str
    end_date: str


class KPISummary(BaseModel):
    """Key performance indicators."""
    fill_rate: Dict[str, Any] = Field(description="Current, target, trend")
    time_to_fill: Dict[str, Any]
    submission_to_hire_ratio: Dict[str, Any]
    cost_per_hire: Dict[str, Any]
    recruiter_productivity: Dict[str, Any] = Field(description="Placements per recruiter")
    offer_acceptance_rate: Dict[str, Any]
    retention_rate_at_90days: Dict[str, Any]


class DashboardOverviewResponse(BaseModel):
    """Combined dashboard overview."""
    overview: OverviewMetrics
    pipeline: PipelineMetrics
    recruiter_performance: RecruiterPerformanceMetrics
    requirements: RequirementAnalytics
    submission_funnel: SubmissionFunnel
    offers: OfferMetrics
    suppliers: SupplierLeaderboard
    sources: CandidateSourceMetrics
    kpis: KPISummary
    generated_at: datetime
    period: str  # "custom", "this_month", "last_month", "this_quarter", etc.
