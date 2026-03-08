"""Pydantic schemas for Advanced Analytics endpoints."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ── Candidate Scorecard Schemas ──
class StrongSkill(BaseModel):
    """Skill candidate excels at."""
    skill: str
    proficiency: int = Field(ge=0, le=100, description="Proficiency score 0-100")
    market_demand: str = Field(description="HIGH/MEDIUM/LOW")


class WeakSkill(BaseModel):
    """Skill candidate lacks or is weak in."""
    skill: str
    importance_for_role: str = Field(description="CRITICAL/IMPORTANT/NICE_TO_HAVE")


class RecommendedJob(BaseModel):
    """Recommended job for candidate."""
    requirement_id: int
    title: str
    match_score: float = Field(ge=0, le=100)
    skill_match: float = Field(ge=0, le=100)
    experience_match: float = Field(ge=0, le=100)


class CandidateScorecardResponse(BaseModel):
    """Full candidate scoring breakdown."""
    candidate_id: int
    candidate_name: str
    candidate_email: str
    overall_score: float = Field(ge=0, le=100)
    skill_score: float = Field(ge=0, le=100)
    experience_score: float = Field(ge=0, le=100)
    education_score: float = Field(ge=0, le=100)
    location_score: float = Field(ge=0, le=100)
    rate_score: float = Field(ge=0, le=100)
    availability_score: float = Field(ge=0, le=100)
    culture_score: float = Field(ge=0, le=100)
    strong_skills: List[StrongSkill]
    weak_skills: List[WeakSkill]
    missing_skills: List[str]
    standout_qualities: List[str]
    recommended_jobs: List[RecommendedJob]
    match_strength: str = Field(description="Strong Match/Good Match/Moderate Match/Weak Match")
    generated_at: datetime


# ── Applicant Tracking Schemas ──
class PipelineStageInfo(BaseModel):
    """Candidate count in a specific pipeline stage."""
    stage: str
    count: int
    days_avg: float = Field(description="Average days in this stage")


class TopCandidateATS(BaseModel):
    """Top candidate for ATS view."""
    candidate_id: int
    name: str
    email: str
    match_score: float = Field(ge=0, le=100)
    current_stage: str
    days_in_stage: int


class ConversionRate(BaseModel):
    """Stage-to-stage conversion metric."""
    from_stage: str
    to_stage: str
    conversion_rate: float = Field(description="Percentage of candidates moving to next stage")


class ApplicantTrackingResponse(BaseModel):
    """ATS tracker for a job."""
    requirement_id: int
    requirement_title: str
    requirement_status: str
    total_applicants: int
    stage_counts: Dict[str, int] = Field(description="Count by stage")
    pipeline_velocity: float = Field(description="Average days per stage")
    bottleneck_stage: Optional[str]
    bottleneck_days: Optional[float]
    top_candidates: List[TopCandidateATS]
    conversion_rates: List[ConversionRate]
    generated_at: datetime


# ── Skill Analysis Schemas ──
class SkillStrength(BaseModel):
    """Skill candidate excels at."""
    skill: str
    proficiency_score: int = Field(ge=0, le=100)
    years_of_experience: Optional[float]


class SkillGap(BaseModel):
    """Skill gap analysis."""
    skill: str
    in_demand: bool = Field(description="Is this skill demanded in matching jobs?")
    frequency_in_jobs: int = Field(description="How many matching jobs require this?")


class DevelopmentRecommendation(BaseModel):
    """Skill development recommendation."""
    skill: str
    priority: str = Field(description="CRITICAL/HIGH/MEDIUM")
    reason: str
    market_demand: str = Field(description="HIGH/MEDIUM/LOW")


class SkillAnalysisResponse(BaseModel):
    """Skill gap analysis for candidate."""
    candidate_id: int
    candidate_name: str
    skill_strengths: List[SkillStrength]
    skill_gaps: List[SkillGap]
    skill_market_demand: Dict[str, str] = Field(description="Skill -> HIGH/MEDIUM/LOW")
    development_recommendations: List[DevelopmentRecommendation]
    generated_at: datetime


# ── Match Insights Schemas ──
class ScoreDistributionBucket(BaseModel):
    """Distribution of scores in a range."""
    range: str = Field(description="e.g., '90-100', '80-89'")
    count: int
    percentage: float


class BestCandidate(BaseModel):
    """Best candidate for a requirement."""
    candidate_id: int
    name: str
    email: str
    overall_score: float = Field(ge=0, le=100)
    skill_score: float = Field(ge=0, le=100)
    experience_score: float = Field(ge=0, le=100)
    education_score: float = Field(ge=0, le=100)
    location_score: float = Field(ge=0, le=100)
    rate_score: float = Field(ge=0, le=100)
    availability_score: float = Field(ge=0, le=100)
    culture_score: float = Field(ge=0, le=100)


class DimensionAverage(BaseModel):
    """Average score for a dimension across all candidates."""
    skill_score: float = Field(ge=0, le=100)
    experience_score: float = Field(ge=0, le=100)
    education_score: float = Field(ge=0, le=100)
    location_score: float = Field(ge=0, le=100)
    rate_score: float = Field(ge=0, le=100)
    availability_score: float = Field(ge=0, le=100)
    culture_score: float = Field(ge=0, le=100)


class MatchInsightsResponse(BaseModel):
    """AI match insights for a job."""
    requirement_id: int
    requirement_title: str
    total_matches: int
    avg_score: float = Field(ge=0, le=100)
    score_distribution: List[ScoreDistributionBucket]
    best_candidates: List[BestCandidate]
    dimension_averages: DimensionAverage
    ai_recommendation: str
    generated_at: datetime


# ── Recruiter Performance Schemas ──
class MonthlyStat(BaseModel):
    """Monthly performance stat."""
    month: str = Field(description="YYYY-MM format")
    submissions: int
    placements: int
    conversion_rate: float


class TopMetric(BaseModel):
    """Top item (skill, client, etc)."""
    name: str
    count: int
    performance_score: Optional[float]


class RecruiterPerformanceResponse(BaseModel):
    """Recruiter performance metrics."""
    recruiter_id: int
    recruiter_name: str
    email: str
    submissions_count: int
    placements_count: int
    conversion_rate: float = Field(description="Percentage of submissions placed")
    avg_time_to_fill: float = Field(description="Days")
    monthly_trend: List[MonthlyStat]
    top_skills_placed: List[TopMetric]
    top_clients: List[TopMetric]
    avg_match_score: float = Field(ge=0, le=100)
    ranking: int = Field(description="Position among all recruiters")
    total_recruiters: int
    generated_at: datetime


# ── Predictions Dashboard Schemas ──
class WorkforceForecast(BaseModel):
    """Workforce forecast for next period."""
    category: str
    forecast_demand: int
    confidence: float = Field(ge=0, le=100, description="Confidence %")


class SupplierPrediction(BaseModel):
    """Supplier fill probability."""
    supplier_id: int
    supplier_name: str
    fill_probability: float = Field(ge=0, le=100)
    expected_placements: int
    tier: str


class SkillShortageAlert(BaseModel):
    """Skills at risk of shortage."""
    skill: str
    demand_trend: str = Field(description="RISING/STABLE/FALLING")
    supply_level: str = Field(description="HIGH/MEDIUM/LOW")
    risk_level: str = Field(description="CRITICAL/HIGH/MEDIUM")


class PredictionsDashboardResponse(BaseModel):
    """AI Predictions Dashboard."""
    workforce_forecast: List[WorkforceForecast]
    supplier_predictions: List[SupplierPrediction]
    skill_shortage_alerts: List[SkillShortageAlert]
    revenue_forecast: float = Field(description="Projected next month revenue")
    revenue_confidence: float = Field(ge=0, le=100, description="Forecast confidence %")
    compliance_risk_alerts: List[Dict[str, Any]]
    generated_at: datetime


# ── Candidate Comparison Schemas ──
class CandidateComparisonRow(BaseModel):
    """Single candidate in comparison."""
    candidate_id: int
    name: str
    email: str
    skill_score: float = Field(ge=0, le=100)
    experience_score: float = Field(ge=0, le=100)
    education_score: float = Field(ge=0, le=100)
    location_score: float = Field(ge=0, le=100)
    rate_score: float = Field(ge=0, le=100)
    availability_score: float = Field(ge=0, le=100)
    culture_score: float = Field(ge=0, le=100)
    overall_score: float = Field(ge=0, le=100)


class DimensionWinner(BaseModel):
    """Which candidate scores highest per dimension."""
    dimension: str
    winner_candidate_id: int
    winner_name: str
    winning_score: float = Field(ge=0, le=100)


class MatchComparisonResponse(BaseModel):
    """Side-by-side candidate comparison."""
    requirement_id: int
    requirement_title: str
    comparison_matrix: List[CandidateComparisonRow]
    winner_by_dimension: List[DimensionWinner]
    overall_winner: str = Field(description="Candidate name with highest overall score")
    overall_winner_id: int
    overall_winner_score: float = Field(ge=0, le=100)
    ai_recommendation: str
    generated_at: datetime
