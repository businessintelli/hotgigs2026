"""Schemas for pipeline analytics, email notifications, and interview feedback."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ── Pipeline Analytics Schemas ──

class PhaseConversion(BaseModel):
    from_phase: str
    to_phase: str
    candidates_entered: int
    candidates_converted: int
    conversion_rate: float = Field(ge=0, le=100)
    avg_time_hours: float
    trend: str = "stable"  # improving, declining, stable

class PipelineFunnel(BaseModel):
    job_id: int
    job_title: str
    phases: List[str]
    phase_counts: Dict[str, int]
    conversions: List[PhaseConversion]
    total_candidates: int
    overall_conversion: float
    bottleneck_phase: Optional[str] = None
    bottleneck_reason: Optional[str] = None
    avg_days_to_hire: float
    generated_at: datetime

class PipelineTrend(BaseModel):
    date: str
    phase_counts: Dict[str, int]
    conversion_rates: Dict[str, float]
    total: int

class PipelineTrendResponse(BaseModel):
    job_id: int
    job_title: str
    trends: List[PipelineTrend]
    period: str

class PhaseBreakdown(BaseModel):
    phase: str
    count: int
    percentage: float
    avg_time_days: float
    top_sources: List[str]

class PipelineCompare(BaseModel):
    job_id: int
    job_title: str
    total: int
    conversion_rate: float
    avg_days_to_hire: float
    phase_counts: Dict[str, int]

class PipelineCompareResponse(BaseModel):
    jobs: List[PipelineCompare]
    best_performing_job: str
    worst_bottleneck: str


# ── Email Notification Schemas ──

class EmailTemplateResponse(BaseModel):
    id: int
    name: str
    trigger_event: str
    subject_template: str
    body_preview: str
    is_active: bool
    variables: Dict[str, Any]

class EmailTemplateCreate(BaseModel):
    name: str
    trigger_event: str
    subject_template: str
    body_html: str
    body_text: str
    variables: Dict[str, Any] = {}

class CandidateNotificationRequest(BaseModel):
    candidate_id: int
    job_id: int
    old_status: Optional[str] = None
    new_status: str
    custom_message: Optional[str] = None

class EmailLogResponse(BaseModel):
    id: int
    candidate_name: str
    candidate_email: str
    job_title: Optional[str]
    notification_type: str
    subject: str
    status: str
    sent_at: datetime
    delivered_at: Optional[datetime]
    opened_at: Optional[datetime]

class NotificationHistoryResponse(BaseModel):
    total_sent: int
    total_delivered: int
    total_opened: int
    delivery_rate: float
    open_rate: float
    logs: List[EmailLogResponse]

class NotificationStats(BaseModel):
    total_sent: int
    by_type: Dict[str, int]
    by_status: Dict[str, int]
    delivery_rate: float
    open_rate: float
    recent_failures: int

class NotificationSettingsResponse(BaseModel):
    auto_notify_on_status_change: bool
    enabled_events: List[str]
    candidate_cc_enabled: bool
    daily_digest: bool
    templates_count: int


# ── Interview Feedback Schemas ──

class RubricCriterion(BaseModel):
    name: str
    description: str
    weight: float = Field(ge=0, le=1, default=0.2)
    scale_labels: Dict[int, str] = {}

class RubricCreate(BaseModel):
    name: str
    description: Optional[str] = None
    job_role: Optional[str] = None
    interview_stage: str = "general"
    criteria: List[RubricCriterion]
    scale_min: int = 1
    scale_max: int = 5

class RubricResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    job_role: Optional[str]
    interview_stage: str
    criteria: List[RubricCriterion]
    scale_min: int
    scale_max: int
    is_active: bool
    version: int

class FeedbackSubmit(BaseModel):
    interview_id: int
    rubric_id: Optional[int] = None
    candidate_id: int
    job_id: int
    interview_stage: str
    criteria_scores: Dict[str, int]
    overall_rating: int = Field(ge=1, le=5)
    recommendation: str = "neutral"
    strengths: List[str] = []
    weaknesses: List[str] = []
    detailed_notes: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: int
    interview_id: int
    interviewer_name: str
    candidate_id: int
    job_id: int
    interview_stage: str
    criteria_scores: Dict[str, int]
    weighted_total: Optional[float]
    overall_rating: int
    recommendation: str
    strengths: List[str]
    weaknesses: List[str]
    detailed_notes: Optional[str]
    is_submitted: bool
    submitted_at: Optional[datetime]

class FeedbackSummary(BaseModel):
    candidate_id: int
    candidate_name: str
    total_interviews: int
    avg_rating: float
    recommendation_breakdown: Dict[str, int]
    criteria_averages: Dict[str, float]
    interviewers: List[str]

class CalibrateResponse(BaseModel):
    interviewer_id: int
    interviewer_name: str
    avg_rating: float
    total_reviews: int
    rating_distribution: Dict[int, int]
    harshness_score: float  # negative = harsh, positive = lenient
    consistency_score: float  # 0-1, higher = more consistent
