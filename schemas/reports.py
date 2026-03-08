"""Pydantic schemas for all report endpoints."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ── Recruiter Leaderboard ──

class RecruiterLeaderboardItem(BaseModel):
    """Single recruiter in the leaderboard."""
    rank: int = Field(description="Ranking position")
    recruiter_name: str = Field(description="Recruiter full name")
    submissions_count: int = Field(description="Total submissions made")
    placements_count: int = Field(description="Total placements")
    conversion_rate: float = Field(description="Submission to placement conversion %")
    avg_time_to_fill_days: float = Field(description="Average days to fill a requirement")
    avg_match_score: float = Field(description="Average match quality score (0-100)")
    revenue_generated: float = Field(description="Total revenue attributed")
    composite_score: float = Field(description="Composite ranking score")


class RecruiterLeaderboardResponse(BaseModel):
    """Recruiter leaderboard report."""
    recruiters: List[RecruiterLeaderboardItem]
    total_recruiters: int
    generated_at: datetime


# ── Source Attribution ──

class SourceAttributionItem(BaseModel):
    """Single recruitment source metrics."""
    source_name: str = Field(description="Source name (LinkedIn, Indeed, Referral, etc.)")
    candidates_sourced: int = Field(description="Total candidates sourced from this source")
    candidates_placed: int = Field(description="Candidates successfully placed")
    conversion_rate: float = Field(description="Sourced to placed conversion %")
    avg_time_to_fill: float = Field(description="Average days from source to placement")
    avg_quality_score: float = Field(description="Average quality score of placements (0-100)")
    cost_per_hire: float = Field(description="Average cost per successful hire")
    roi_score: float = Field(description="Return on investment score")


class SourceAttributionResponse(BaseModel):
    """Source attribution report."""
    sources: List[SourceAttributionItem]
    total_candidates_sourced: int
    total_candidates_placed: int
    overall_conversion_rate: float
    generated_at: datetime


# ── Cost Analytics ──

class CostByClient(BaseModel):
    """Cost metrics per client."""
    client_name: str
    total_cost: float
    total_billing: float
    placements: int
    cost_per_placement: float


class CostByDepartment(BaseModel):
    """Cost metrics per department."""
    department: str
    total_cost: float
    total_billing: float
    placements: int
    cost_per_placement: float


class CostTrendMonth(BaseModel):
    """Monthly cost trend data."""
    month: str = Field(description="YYYY-MM format")
    total_cost: float
    total_billing: float
    gross_profit: float
    margin_percent: float


class SkillMargin(BaseModel):
    """Margin analysis by skill category."""
    skill_category: str
    avg_margin_percent: float
    placements: int
    total_billing: float


class CostAnalyticsResponse(BaseModel):
    """Cost analytics report."""
    overall_cost_per_hire: float
    avg_margin_percent: float
    total_billing: float
    total_cost: float
    gross_profit: float
    cost_by_client: List[CostByClient]
    cost_by_department: List[CostByDepartment]
    cost_trend: List[CostTrendMonth]
    margin_by_skill: List[SkillMargin]
    generated_at: datetime


# ── Diversity Analytics ──

class DiversityByStage(BaseModel):
    """Diversity representation at each pipeline stage."""
    stage: str
    total_count: int
    diverse_count: int
    diverse_percent: float


class HiringRateByCategory(BaseModel):
    """Hiring rate by diversity category."""
    category: str
    pipeline_representation: float
    hired_representation: float
    hiring_rate: float


class InterviewToOfferRatio(BaseModel):
    """Interview to offer conversion by category."""
    category: str
    interviews: int
    offers: int
    conversion_rate: float


class SourceDiversityBreakdown(BaseModel):
    """Diversity of candidates by source."""
    source: str
    total_candidates: int
    diverse_candidates: int
    diverse_percent: float


class DiversityAnalyticsResponse(BaseModel):
    """Diversity analytics report (anonymized and aggregated)."""
    note: str = Field(default="All data anonymized and aggregated. No individual identification.")
    pipeline_diversity: List[DiversityByStage]
    hiring_rate_by_category: List[HiringRateByCategory]
    interview_to_offer_ratio: List[InterviewToOfferRatio]
    source_diversity: List[SourceDiversityBreakdown]
    generated_at: datetime


# ── Time Analytics ──

class TimeToFillByPriority(BaseModel):
    """Time to fill metrics by requirement priority."""
    priority: str
    avg_days: float
    min_days: int
    max_days: int
    count: int


class TimeToFillBySkill(BaseModel):
    """Time to fill by skill category."""
    skill_category: str
    avg_days: float
    count: int


class TimeToFillByClient(BaseModel):
    """Time to fill by client."""
    client_name: str
    avg_days: float
    count: int


class TimeToFillTrendMonth(BaseModel):
    """Monthly time to fill trend."""
    month: str = Field(description="YYYY-MM format")
    avg_days: float
    count: int


class BottleneckAnalysis(BaseModel):
    """Pipeline stage bottleneck analysis."""
    stage: str
    avg_days_in_stage: float
    total_candidates: int
    candidates_stuck_7plus_days: int


class TimeAnalyticsResponse(BaseModel):
    """Time-to-fill analytics report."""
    overall_avg_ttf_days: float
    ttf_by_priority: List[TimeToFillByPriority]
    ttf_by_skill_category: List[TimeToFillBySkill]
    ttf_by_client: List[TimeToFillByClient]
    ttf_trend_monthly: List[TimeToFillTrendMonth]
    bottleneck_analysis: List[BottleneckAnalysis]
    generated_at: datetime


# ── Pipeline Aging ──

class AgingByStage(BaseModel):
    """Aging analysis per pipeline stage."""
    stage: str
    total_candidates: int
    aging_7_plus_days: int
    aging_14_plus_days: int
    aging_30_plus_days: int


class StaleRequirement(BaseModel):
    """Requirement that is open for too long."""
    requirement_id: str
    requisition_title: str
    open_days: int
    submissions_count: int
    client_name: str


class AtRiskCandidate(BaseModel):
    """Candidate with no recent activity."""
    candidate_id: str
    candidate_name: str
    current_stage: str
    days_inactive: int
    requirement: str


class PipelineAgingResponse(BaseModel):
    """Pipeline aging report."""
    aging_by_stage: List[AgingByStage]
    stale_requirements: List[StaleRequirement] = Field(
        description="Requirements open >30 days with <3 submissions"
    )
    at_risk_candidates: List[AtRiskCandidate] = Field(
        description="Candidates with no activity >14 days"
    )
    generated_at: datetime


# ── MSP Executive Summary ──

class RevenueByClient(BaseModel):
    """Revenue metrics for top clients."""
    rank: int
    client_name: str
    revenue: float
    placements: int
    margin_percent: float


class FillRateBySupplier(BaseModel):
    """Fill rate metrics for top suppliers."""
    rank: int
    supplier_name: str
    fill_rate: float
    placements: int
    avg_quality_score: float


class MSPExecutiveSummaryResponse(BaseModel):
    """MSP executive summary report."""
    total_active_clients: int
    total_active_suppliers: int
    total_active_placements: int
    revenue_by_client: List[RevenueByClient] = Field(description="Top 5 clients by revenue")
    fill_rate_by_supplier: List[FillRateBySupplier] = Field(description="Top 5 suppliers by fill rate")
    sla_compliance_rate: float
    compliance_overall_score: float
    month_over_month_growth: float = Field(description="Growth % compared to previous month")
    projected_quarterly_revenue: float
    generated_at: datetime
