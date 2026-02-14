from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List
from models.enums import InterviewType, InterviewStatus
from schemas.common import BaseResponse


class InterviewCreate(BaseModel):
    """Interview creation schema."""

    candidate_id: int
    requirement_id: int
    interview_type: InterviewType
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(default=None, ge=1)
    interviewer_name: Optional[str] = Field(default=None, max_length=255)
    interviewer_email: Optional[str] = Field(default=None, max_length=255)
    meeting_link: Optional[str] = Field(default=None, max_length=500)
    notes: Optional[str] = None
    metadata: Optional[dict] = Field(default_factory=dict)


class InterviewUpdate(BaseModel):
    """Interview update schema."""

    interview_type: Optional[InterviewType] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(default=None, ge=1)
    status: Optional[InterviewStatus] = None
    interviewer_name: Optional[str] = Field(default=None, max_length=255)
    interviewer_email: Optional[str] = Field(default=None, max_length=255)
    meeting_link: Optional[str] = Field(default=None, max_length=500)
    recording_url: Optional[str] = Field(default=None, max_length=500)
    transcript_url: Optional[str] = Field(default=None, max_length=500)
    notes: Optional[str] = None
    metadata: Optional[dict] = None
    is_active: Optional[bool] = None


class InterviewResponse(BaseResponse):
    """Interview response schema."""

    candidate_id: int
    requirement_id: int
    interview_type: InterviewType
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    status: InterviewStatus
    interviewer_name: Optional[str] = None
    interviewer_email: Optional[str] = None
    meeting_link: Optional[str] = None
    recording_url: Optional[str] = None
    transcript_url: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class InterviewFeedbackCreate(BaseModel):
    """Interview feedback creation schema."""

    interview_id: int
    evaluator: Optional[str] = Field(default=None, max_length=255)
    overall_rating: Optional[int] = Field(default=None, ge=1, le=5)
    technical_rating: Optional[int] = Field(default=None, ge=1, le=5)
    communication_rating: Optional[int] = Field(default=None, ge=1, le=5)
    culture_fit_rating: Optional[int] = Field(default=None, ge=1, le=5)
    problem_solving_rating: Optional[int] = Field(default=None, ge=1, le=5)
    strengths: Optional[List[str]] = Field(default_factory=list)
    weaknesses: Optional[List[str]] = Field(default_factory=list)
    recommendation: Optional[str] = Field(default=None, max_length=50)
    detailed_notes: Optional[str] = None
    scorecard_data: Optional[dict] = Field(default_factory=dict)
    ai_generated: Optional[bool] = Field(default=False)


class InterviewFeedbackResponse(BaseResponse):
    """Interview feedback response schema."""

    interview_id: int
    evaluator: Optional[str] = None
    overall_rating: Optional[int] = None
    technical_rating: Optional[int] = None
    communication_rating: Optional[int] = None
    culture_fit_rating: Optional[int] = None
    problem_solving_rating: Optional[int] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    recommendation: Optional[str] = None
    detailed_notes: Optional[str] = None
    scorecard_data: Optional[dict] = None
    ai_generated: bool

    class Config:
        from_attributes = True
