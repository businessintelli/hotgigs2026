"""ATS schemas for Enhanced ATS module."""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field
from models.enums import (
    JobOrderPriority,
    JobOrderDistribution,
    JobOrderStatus,
    OfferStatus,
    OnboardingTaskType,
    OnboardingTaskStatus,
    InterviewRecommendation,
)


# ── JobOrder Schemas ──

class JobOrderCreate(BaseModel):
    """Create job order."""
    requirement_id: int
    client_org_id: Optional[int] = None
    priority: JobOrderPriority = JobOrderPriority.NORMAL
    target_fill_date: Optional[date] = None
    max_submissions: int = 5
    distribution_type: JobOrderDistribution = JobOrderDistribution.OPEN
    distributed_to: Optional[List[int]] = Field(default_factory=list)


class JobOrderUpdate(BaseModel):
    """Update job order."""
    priority: Optional[JobOrderPriority] = None
    target_fill_date: Optional[date] = None
    max_submissions: Optional[int] = None
    status: Optional[JobOrderStatus] = None
    cancelled_reason: Optional[str] = None


class JobOrderResponse(BaseModel):
    """Job order response."""
    id: int
    requirement_id: int
    client_org_id: Optional[int]
    priority: JobOrderPriority
    target_fill_date: Optional[date]
    max_submissions: int
    distribution_type: JobOrderDistribution
    distributed_to: Optional[List[int]]
    status: JobOrderStatus
    filled_at: Optional[datetime]
    cancelled_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── OfferWorkflow Schemas ──

class OfferWorkflowCreate(BaseModel):
    """Create offer workflow."""
    submission_id: int
    candidate_id: int
    bill_rate: Optional[float] = None
    pay_rate: Optional[float] = None
    start_date: date
    end_date: Optional[date] = None
    benefits_package: Optional[str] = None
    expiry_date: Optional[date] = None


class OfferWorkflowUpdate(BaseModel):
    """Update offer workflow."""
    offer_status: Optional[OfferStatus] = None
    bill_rate: Optional[float] = None
    pay_rate: Optional[float] = None
    approved_by: Optional[int] = None
    decline_reason: Optional[str] = None
    counter_offer_details: Optional[dict] = None
    expiry_date: Optional[date] = None


class OfferWorkflowResponse(BaseModel):
    """Offer workflow response."""
    id: int
    submission_id: int
    candidate_id: int
    offer_status: OfferStatus
    bill_rate: Optional[float]
    pay_rate: Optional[float]
    start_date: date
    end_date: Optional[date]
    benefits_package: Optional[str]
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    extended_at: Optional[datetime]
    responded_at: Optional[datetime]
    decline_reason: Optional[str]
    counter_offer_details: Optional[dict]
    expiry_date: Optional[date]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── OnboardingTask Schemas ──

class OnboardingTaskCreate(BaseModel):
    """Create onboarding task."""
    candidate_id: int
    placement_id: Optional[int] = None
    task_name: str = Field(..., min_length=1, max_length=255)
    task_type: OnboardingTaskType
    assigned_to: Optional[int] = None
    due_date: Optional[date] = None


class OnboardingTaskUpdate(BaseModel):
    """Update onboarding task."""
    status: Optional[OnboardingTaskStatus] = None
    assigned_to: Optional[int] = None
    due_date: Optional[date] = None
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None


class OnboardingTaskResponse(BaseModel):
    """Onboarding task response."""
    id: int
    candidate_id: int
    placement_id: Optional[int]
    task_name: str
    task_type: OnboardingTaskType
    status: OnboardingTaskStatus
    assigned_to: Optional[int]
    due_date: Optional[date]
    completed_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── InterviewFeedback Schemas ──

class InterviewFeedbackCreate(BaseModel):
    """Create interview feedback."""
    interview_id: Optional[int] = None
    submission_id: Optional[int] = None
    candidate_id: int
    interviewer_id: int
    overall_rating: int = Field(..., ge=1, le=5)
    technical_score: Optional[int] = Field(None, ge=0, le=100)
    communication_score: Optional[int] = Field(None, ge=0, le=100)
    culture_fit_score: Optional[int] = Field(None, ge=0, le=100)
    problem_solving_score: Optional[int] = Field(None, ge=0, le=100)
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    recommendation: InterviewRecommendation
    detailed_notes: Optional[str] = None
    is_anonymous: bool = False


class InterviewFeedbackUpdate(BaseModel):
    """Update interview feedback."""
    overall_rating: Optional[int] = None
    technical_score: Optional[int] = None
    communication_score: Optional[int] = None
    culture_fit_score: Optional[int] = None
    problem_solving_score: Optional[int] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    recommendation: Optional[InterviewRecommendation] = None
    detailed_notes: Optional[str] = None


class InterviewFeedbackResponse(BaseModel):
    """Interview feedback response."""
    id: int
    interview_id: Optional[int]
    submission_id: Optional[int]
    candidate_id: int
    interviewer_id: int
    overall_rating: int
    technical_score: Optional[int]
    communication_score: Optional[int]
    culture_fit_score: Optional[int]
    problem_solving_score: Optional[int]
    strengths: Optional[str]
    weaknesses: Optional[str]
    recommendation: InterviewRecommendation
    detailed_notes: Optional[str]
    is_anonymous: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Feedback Summary ──

class FeedbackSummaryResponse(BaseModel):
    """Aggregated feedback summary for a submission."""
    submission_id: int
    candidate_id: int
    total_feedback_count: int
    avg_overall_rating: float
    avg_technical_score: Optional[float]
    avg_communication_score: Optional[float]
    avg_culture_fit_score: Optional[float]
    avg_problem_solving_score: Optional[float]
    recommendation_counts: dict = Field(
        default_factory=dict,
        description="Count of each recommendation type",
    )
    consensus_recommendation: Optional[InterviewRecommendation]
    last_feedback_at: Optional[datetime]


# ── Onboarding Dashboard ──

class OnboardingDashboardResponse(BaseModel):
    """Onboarding overview dashboard."""
    pending_count: int
    in_progress_count: int
    completed_count: int
    blocked_count: int
    waived_count: int
    overdue_count: int
    upcoming_due_count: int
    total_count: int
    completion_rate: float = Field(..., ge=0.0, le=100.0)
