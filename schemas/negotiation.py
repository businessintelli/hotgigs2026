"""Pydantic schemas for rate negotiation and interview scheduling."""

from pydantic import BaseModel, Field
from datetime import datetime, date, time
from typing import Optional, List, Dict, Any
from schemas.common import BaseResponse


# ===== Rate Negotiation Schemas =====


class NegotiationRoundCreate(BaseModel):
    """Create a negotiation round."""

    negotiation_id: int
    proposed_by: str = Field(..., min_length=1, max_length=50)  # recruiter/candidate/customer/ai
    proposed_rate: float = Field(..., gt=0)
    rate_type: str = Field(..., min_length=1, max_length=50)
    notes: Optional[str] = Field(None, max_length=1000)


class NegotiationRoundUpdate(BaseModel):
    """Update negotiation round with counter offer."""

    counter_rate: Optional[float] = Field(None, gt=0)
    counter_notes: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None, max_length=50)


class NegotiationRoundResponse(BaseResponse):
    """Negotiation round response."""

    negotiation_id: int
    round_number: int
    proposed_by: str
    proposed_rate: float
    rate_type: str
    notes: Optional[str] = None
    counter_rate: Optional[float] = None
    counter_notes: Optional[str] = None
    status: str
    proposed_at: datetime
    responded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RateNegotiationCreate(BaseModel):
    """Create a new rate negotiation."""

    submission_id: int
    initial_offer: float = Field(..., gt=0)
    rate_type: str = Field(..., min_length=1, max_length=50)
    candidate_desired_rate: Optional[float] = Field(None, gt=0)
    customer_max_rate: Optional[float] = Field(None, gt=0)
    target_margin_percentage: float = Field(default=20.0, ge=0, le=100)
    bill_rate: Optional[float] = Field(None, gt=0)
    pay_rate: Optional[float] = Field(None, gt=0)


class RateNegotiationUpdate(BaseModel):
    """Update negotiation."""

    current_proposed_rate: Optional[float] = Field(None, gt=0)
    status: Optional[str] = Field(None, max_length=50)
    closed_reason: Optional[str] = Field(None, max_length=255)


class RateNegotiationResponse(BaseResponse):
    """Rate negotiation response."""

    submission_id: int
    candidate_id: int
    requirement_id: int
    customer_id: int
    candidate_desired_rate: Optional[float] = None
    customer_max_rate: Optional[float] = None
    initial_proposed_rate: float
    current_proposed_rate: float
    agreed_rate: Optional[float] = None
    rate_type: str
    bill_rate: Optional[float] = None
    pay_rate: Optional[float] = None
    margin: Optional[float] = None
    margin_percentage: Optional[float] = None
    target_margin_percentage: float
    status: str
    total_rounds: int
    max_rounds: int
    started_at: datetime
    closed_at: Optional[datetime] = None
    closed_reason: Optional[str] = None
    negotiated_by: Optional[int] = None
    rounds: List[NegotiationRoundResponse] = []

    class Config:
        from_attributes = True


class RateEvaluationResponse(BaseModel):
    """Rate evaluation result."""

    proposed_rate: float
    bill_rate: float
    pay_rate: float
    margin_amount: float
    margin_percentage: float
    target_margin_percentage: float
    is_acceptable: bool
    feedback: str
    recommendations: List[str]


class AutoNegotiateResponse(BaseModel):
    """AI-powered negotiation suggestion."""

    suggested_rate: float
    rate_type: str
    reasoning: str
    confidence_score: float = Field(..., ge=0, le=1)
    market_comparison: Dict[str, Any]
    next_steps: List[str]


# ===== Interview Scheduling Schemas =====


class ParticipantModel(BaseModel):
    """Interview participant."""

    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., max_length=255)
    role: str = Field(..., min_length=1, max_length=100)


class InterviewScheduleCreate(BaseModel):
    """Create interview schedule."""

    interview_id: Optional[int] = None
    candidate_id: int
    requirement_id: int
    interview_type: str = Field(..., min_length=1, max_length=50)
    scheduled_date: str = Field(..., min_length=10, max_length=10)  # YYYY-MM-DD
    scheduled_time: str = Field(..., min_length=5, max_length=5)    # HH:MM
    timezone: str = Field(default="UTC", max_length=50)
    duration_minutes: int = Field(default=60, gt=0)
    interviewer_name: str = Field(..., min_length=1, max_length=255)
    interviewer_email: str = Field(..., max_length=255)
    additional_participants: Optional[List[ParticipantModel]] = None
    meeting_link: Optional[str] = Field(None, max_length=500)
    meeting_id: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)


class InterviewScheduleUpdate(BaseModel):
    """Update interview schedule."""

    scheduled_date: Optional[str] = Field(None, min_length=10, max_length=10)
    scheduled_time: Optional[str] = Field(None, min_length=5, max_length=5)
    timezone: Optional[str] = Field(None, max_length=50)
    duration_minutes: Optional[int] = Field(None, gt=0)
    interviewer_name: Optional[str] = Field(None, max_length=255)
    interviewer_email: Optional[str] = Field(None, max_length=255)
    meeting_link: Optional[str] = Field(None, max_length=500)
    meeting_id: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)


class InterviewRescheduleRequest(BaseModel):
    """Request to reschedule interview."""

    scheduled_date: str = Field(..., min_length=10, max_length=10)
    scheduled_time: str = Field(..., min_length=5, max_length=5)
    reason: str = Field(..., min_length=1, max_length=500)


class InterviewCancelRequest(BaseModel):
    """Request to cancel interview."""

    reason: str = Field(..., min_length=1, max_length=500)


class InterviewScheduleResponse(BaseResponse):
    """Interview schedule response."""

    interview_id: Optional[int] = None
    candidate_id: int
    requirement_id: int
    interview_type: str
    scheduled_date: str
    scheduled_time: str
    timezone: str
    duration_minutes: int
    interviewer_name: str
    interviewer_email: str
    additional_participants: Optional[List[Dict[str, str]]] = None
    meeting_link: Optional[str] = None
    meeting_id: Optional[str] = None
    location: Optional[str] = None
    status: str
    confirmation_status: Optional[Dict[str, str]] = None
    reschedule_count: int
    reschedule_history: Optional[List[Dict[str, Any]]] = None
    calendar_event_id: Optional[str] = None
    calendar_provider: Optional[str] = None
    reminder_sent: bool
    reminder_sent_at: Optional[datetime] = None
    notes: Optional[str] = None
    cancellation_reason: Optional[str] = None
    scheduled_by: Optional[int] = None

    class Config:
        from_attributes = True


class AvailabilitySlot(BaseModel):
    """Available time slot for meeting."""

    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    timezone: str
    duration_minutes: int
    available_participants: List[str]


class AvailabilityCheckRequest(BaseModel):
    """Check availability for participants."""

    participant_emails: List[str] = Field(..., min_items=1)
    date_range_start: str = Field(..., min_length=10, max_length=10)
    date_range_end: str = Field(..., min_length=10, max_length=10)
    duration_minutes: int = Field(default=60, gt=0)
    preferred_times: Optional[List[str]] = None
    timezone: str = Field(default="UTC", max_length=50)


class AvailabilityCheckResponse(BaseModel):
    """Availability check result."""

    participant_emails: List[str]
    date_range_start: str
    date_range_end: str
    availability_status: Dict[str, bool]  # {email: is_available}
    available_slots: List[AvailabilitySlot]
    conflicts: Optional[Dict[str, List[str]]] = None


class SchedulingAnalyticsResponse(BaseModel):
    """Scheduling analytics."""

    total_interviews_scheduled: int
    rescheduled_count: int
    rescheduled_percentage: float
    no_show_count: int
    no_show_percentage: float
    average_days_to_schedule: float
    popular_time_slots: Dict[str, int]
    popular_interview_types: Dict[str, int]
    average_reschedules_per_interview: float
    cancellation_reasons: Dict[str, int]
