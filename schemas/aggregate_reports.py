"""Aggregate reports response schemas for comprehensive HR analytics."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════════
# 1. CLIENT PERFORMANCE REPORT SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class ClientMetricItem(BaseModel):
    """Single client performance metrics."""
    client_id: int
    client_name: str
    organization_type: str = "CLIENT"
    total_jobs_posted: int
    active_jobs: int
    total_submissions_received: int
    interviews_conducted: int
    offers_extended: int
    placements_made: int
    avg_time_to_fill_days: float
    fill_rate_percent: float
    avg_match_score: float = Field(description="Average candidate match score 0-100")
    total_spend: float = Field(description="Total billing amount")
    satisfaction_score: float = Field(description="Client satisfaction 0-5 stars")
    contract_value: float
    active_contracts: int
    top_job_title: Optional[str] = None
    pipeline_count: int


class ClientPerformanceReport(BaseModel):
    """Client performance report with summary."""
    clients: List[ClientMetricItem]
    summary: Dict[str, Any] = Field(description="Totals and averages across all clients")
    report_period: str
    generated_at: datetime


# ═══════════════════════════════════════════════════════════════════════════
# 2. CLIENT JOB BREAKDOWN SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class CandidateSummary(BaseModel):
    """Brief candidate info for job breakdown."""
    candidate_id: int
    candidate_name: str
    match_score: float
    current_phase: str
    source: str


class JobForClient(BaseModel):
    """Single job stats for a client."""
    job_id: int
    job_title: str
    location: str
    priority: str
    bill_rate: float
    submissions_count: int
    interviews_count: int
    shortlisted_count: int
    offers_count: int
    placements_count: int
    days_open: int
    current_status: str
    avg_candidate_score: float
    top_3_candidates: List[CandidateSummary]


class ClientJobBreakdown(BaseModel):
    """Job breakdown for a specific client."""
    client_id: int
    client_name: str
    total_jobs: int
    active_jobs: int
    filled_jobs: int
    jobs: List[JobForClient]
    report_period: str
    generated_at: datetime


# ═══════════════════════════════════════════════════════════════════════════
# 3. JOB PERFORMANCE REPORT SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class PhaseBreakdown(BaseModel):
    """Candidate count by phase."""
    phase: str
    count: int
    days_in_phase_avg: float


class JobMetricItem(BaseModel):
    """Single job performance metrics."""
    job_id: int
    job_title: str
    client_name: str
    location: str
    priority: str
    bill_rate: float
    total_applicants: int
    phase_breakdown: List[PhaseBreakdown] = Field(description="Sourced, screening, submitted, etc.")
    conversion_rate_percent: float = Field(description="From applicant to placement")
    avg_time_in_phase_days: float
    days_open: int
    fill_status: str
    filled_count: int


class JobPerformanceReport(BaseModel):
    """Job performance report with all jobs."""
    jobs: List[JobMetricItem]
    total_jobs: int
    avg_fill_rate: float
    avg_time_to_fill: float
    report_period: str
    generated_at: datetime


# ═══════════════════════════════════════════════════════════════════════════
# 4. JOB APPLICANT BREAKDOWN SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class MatchDimension(BaseModel):
    """Match score by dimension."""
    dimension: str
    score: float


class PhaseHistory(BaseModel):
    """Phase transition history."""
    phase: str
    entered_date: datetime
    exited_date: Optional[datetime] = None
    days_in_phase: int


class ApplicantDetail(BaseModel):
    """Single applicant detail."""
    applicant_id: int
    candidate_name: str
    current_phase: str
    overall_match_score: float
    match_dimensions: List[MatchDimension] = Field(description="Skills, experience, location, etc.")
    skills: List[str]
    source: str
    time_in_current_phase_days: int
    phase_history: List[PhaseHistory]
    recruiter_assigned: Optional[str] = None


class JobApplicantBreakdown(BaseModel):
    """Applicant breakdown for a specific job."""
    job_id: int
    job_title: str
    client_name: str
    total_applicants: int
    applicants: List[ApplicantDetail]
    report_period: str
    generated_at: datetime


# ═══════════════════════════════════════════════════════════════════════════
# 5. SUPPLIER PERFORMANCE REPORT SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class SupplierMetricItem(BaseModel):
    """Single supplier performance metrics."""
    supplier_id: int
    supplier_name: str
    organization_type: str = "SUPPLIER"
    tier: str  # Gold, Silver, Bronze
    total_candidates_submitted: int
    placements_made: int
    fill_rate_percent: float
    avg_match_score_submissions: float
    avg_time_to_submit_days: float
    rejection_rate_percent: float
    interview_to_offer_rate_percent: float
    quality_score: float = Field(description="0-100 based on submissions quality")
    compliance_score: float = Field(description="0-100 based on SLA adherence")
    total_revenue_generated: float
    active_contracts: int
    sla_adherence_percent: float


class SupplierPerformanceReport(BaseModel):
    """Supplier performance report with summary."""
    suppliers: List[SupplierMetricItem]
    summary: Dict[str, Any] = Field(description="Totals and averages across suppliers")
    report_period: str
    generated_at: datetime


# ═══════════════════════════════════════════════════════════════════════════
# 6. SUPPLIER JOB BREAKDOWN SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class SupplierJobSubmission(BaseModel):
    """Job submission stats from supplier."""
    job_id: int
    job_title: str
    client_name: str
    candidates_submitted: int
    shortlisted_count: int
    placed_count: int
    avg_score: float
    best_candidate_name: Optional[str] = None
    rejection_reasons: Dict[str, int] = Field(description="Reason to count mapping")


class SupplierJobBreakdown(BaseModel):
    """Job breakdown for a specific supplier."""
    supplier_id: int
    supplier_name: str
    tier: str
    total_jobs_submitted_to: int
    total_placements: int
    jobs: List[SupplierJobSubmission]
    report_period: str
    generated_at: datetime


# ═══════════════════════════════════════════════════════════════════════════
# 7. RECRUITER PERFORMANCE REPORT SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class MonthlyTrend(BaseModel):
    """Monthly submissions/placements trend."""
    month: str  # YYYY-MM format
    submissions: int
    placements: int
    conversion_rate: float


class RecruiterMetricItem(BaseModel):
    """Single recruiter performance metrics."""
    recruiter_id: int
    recruiter_name: str
    email: str
    total_submissions: int
    placements_made: int
    conversion_rate_percent: float
    avg_time_to_submit_days: float
    avg_match_score: float
    revenue_generated: float = Field(description="Total placement value generated")
    active_requisitions: int
    candidates_in_pipeline_by_phase: Dict[str, int]
    top_skills_handled: List[str]
    top_clients_served: List[str]
    month_over_month_trends: List[MonthlyTrend] = Field(description="Last 6 months")


class RecruiterPerformanceReport(BaseModel):
    """Recruiter performance report with all recruiters."""
    recruiters: List[RecruiterMetricItem]
    total_recruiters: int
    avg_conversion_rate: float
    avg_submissions_per_recruiter: float
    top_recruiter_id: Optional[int] = None
    report_period: str
    generated_at: datetime


# ═══════════════════════════════════════════════════════════════════════════
# 8. RECRUITER ACTIVITY BREAKDOWN SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class DailyActivityData(BaseModel):
    """Daily activity metrics."""
    date: str  # YYYY-MM-DD
    submissions_count: int
    placements_count: int
    interviews_scheduled: int


class SourceingChannelBreakdown(BaseModel):
    """Candidates sourced by channel."""
    channel: str
    candidates_sourced: int
    placements_from_channel: int
    quality_score: float


class RecruiterActivity(BaseModel):
    """Detailed recruiter activity."""
    recruiter_id: int
    recruiter_name: str
    daily_activity: List[DailyActivityData] = Field(description="Last 30 days")
    weekly_submission_avg: float
    placement_velocity_placements_per_week: float
    candidate_sourcing_by_channel: List[SourceingChannelBreakdown]
    interview_scheduling_rate: float = Field(description="% of submissions interviewed")
    offer_acceptance_rate_percent: float
    pipeline_health: Dict[str, int] = Field(description="Active, stale, etc.")
    stale_candidates_count: int = Field(description="No activity >30 days")
    report_period: str
    generated_at: datetime


# ═══════════════════════════════════════════════════════════════════════════
# 9. COMPANY-WIDE EXECUTIVE REPORT SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class TopPerformer(BaseModel):
    """Top performer in a category."""
    id: int
    name: str
    metric_value: float


class DepartmentBreakdown(BaseModel):
    """Department hiring stats."""
    department: str
    active_jobs: int
    filled_jobs: int
    placements_ytd: int
    avg_time_to_fill_days: float


class CompanyExecutiveReport(BaseModel):
    """Organization-wide executive summary."""
    organization_name: str
    total_active_jobs: int
    total_candidates_in_pipeline: int
    total_placements_ytd: int
    avg_time_to_fill_days: float
    avg_cost_per_hire: float
    fill_rate_percent: float
    offer_acceptance_rate_percent: float
    top_performing_clients: List[TopPerformer]
    top_performing_suppliers: List[TopPerformer]
    top_performing_recruiters: List[TopPerformer]
    month_over_month_trends: List[MonthlyTrend] = Field(description="Last 6 months: placements trend")
    department_breakdown: List[DepartmentBreakdown]
    total_revenue_ytd: float
    cost_per_fill_avg: float
    report_period: str
    generated_at: datetime


# ═══════════════════════════════════════════════════════════════════════════
# 10. CROSS-DIMENSIONAL MATRIX SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class CrossDimensionalMatrix(BaseModel):
    """Cross-dimensional analytics matrix."""
    client_supplier_placements: Dict[str, Dict[str, int]] = Field(
        description="Client name -> {supplier name -> placement count}"
    )
    client_recruiter_performance: Dict[str, Dict[str, float]] = Field(
        description="Client name -> {recruiter name -> placement count}"
    )
    supplier_skill_strength: Dict[str, Dict[str, int]] = Field(
        description="Supplier name -> {skill -> submission count}"
    )
    job_priority_ttf: Dict[str, float] = Field(
        description="Priority level -> avg time to fill days"
    )
    source_conversion_rate: Dict[str, float] = Field(
        description="Source -> conversion rate %"
    )
    location_fill_rate: Dict[str, float] = Field(
        description="Location -> fill rate %"
    )
    report_period: str
    generated_at: datetime


# ═══════════════════════════════════════════════════════════════════════════
# 11. PIPELINE VELOCITY REPORT SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class PhaseVelocity(BaseModel):
    """Velocity metrics for a phase."""
    from_phase: str
    to_phase: str
    avg_days: float
    median_days: float
    conversion_rate_percent: float


class VelocityBreakdown(BaseModel):
    """Velocity breakdown by dimension."""
    dimension: str  # client, priority, job_type
    dimension_value: str
    phase_velocities: List[PhaseVelocity]


class WeeklyVelocityTrend(BaseModel):
    """Weekly velocity trend."""
    week: str  # YYYY-WW format
    avg_time_across_all_phases: float


class PipelineVelocityReport(BaseModel):
    """Pipeline velocity and phase progression."""
    overall_phase_velocities: List[PhaseVelocity]
    bottleneck_phase: Optional[str] = None
    bottleneck_avg_days: Optional[float] = None
    velocity_by_client: List[VelocityBreakdown]
    velocity_by_priority: List[VelocityBreakdown]
    velocity_by_job_type: List[VelocityBreakdown]
    week_over_week_trends: List[WeeklyVelocityTrend] = Field(description="Last 12 weeks")
    report_period: str
    generated_at: datetime


# ═══════════════════════════════════════════════════════════════════════════
# 12. CONVERSION FUNNEL SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class FunnelStage(BaseModel):
    """Single funnel stage."""
    stage: str
    count: int
    conversion_from_start_percent: float = Field(description="% of initial sourced")
    dropoff_from_previous_percent: float = Field(description="% lost from previous stage")
    avg_days_to_this_stage: float


class ClientFunnelBreakdown(BaseModel):
    """Funnel breakdown for a client."""
    client_name: str
    stages: List[FunnelStage]
    overall_conversion_percent: float


class SupplierFunnelBreakdown(BaseModel):
    """Funnel breakdown for a supplier."""
    supplier_name: str
    stages: List[FunnelStage]
    overall_conversion_percent: float


class MonthFunnelTrend(BaseModel):
    """Monthly funnel trend."""
    month: str  # YYYY-MM
    sourced_count: int
    screening_count: int
    submitted_count: int
    interviewed_count: int
    offered_count: int
    placed_count: int


class ConversionFunnelReport(BaseModel):
    """Full conversion funnel from sourcing to placement."""
    overall_funnel: List[FunnelStage] = Field(description="Sourced → Screening → Submitted → Interview → Offer → Placed")
    overall_conversion_rate: float = Field(description="Placed / Sourced %")
    by_client: List[ClientFunnelBreakdown]
    by_supplier: List[SupplierFunnelBreakdown]
    month_trends: List[MonthFunnelTrend] = Field(description="Last 6 months")
    report_period: str
    generated_at: datetime
