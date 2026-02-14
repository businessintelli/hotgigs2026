from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
from models.enums import SubmissionStatus
from schemas.common import BaseResponse


class SubmissionCreate(BaseModel):
    """Submission creation schema."""

    requirement_id: int
    candidate_id: int
    customer_id: int
    match_score_id: Optional[int] = None
    submitted_by: int
    internal_notes: Optional[str] = None
    customer_notes: Optional[str] = None
    resume_version_used: Optional[int] = Field(default=1, ge=1)
    rate_proposed: Optional[float] = Field(default=None, ge=0)
    metadata: Optional[dict] = Field(default_factory=dict)


class SubmissionUpdate(BaseModel):
    """Submission update schema."""

    status: Optional[SubmissionStatus] = None
    internal_notes: Optional[str] = None
    customer_notes: Optional[str] = None
    resume_version_used: Optional[int] = Field(default=None, ge=1)
    rate_proposed: Optional[float] = Field(default=None, ge=0)
    reviewed_by: Optional[int] = None
    customer_response: Optional[str] = Field(default=None, max_length=500)
    rejection_reason: Optional[str] = None
    metadata: Optional[dict] = None
    is_active: Optional[bool] = None


class SubmissionResponse(BaseResponse):
    """Submission response schema."""

    requirement_id: int
    candidate_id: int
    customer_id: int
    match_score_id: Optional[int] = None
    submitted_by: int
    status: SubmissionStatus
    internal_notes: Optional[str] = None
    customer_notes: Optional[str] = None
    resume_version_used: Optional[int] = None
    rate_proposed: Optional[float] = None
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    submitted_to_customer_at: Optional[datetime] = None
    customer_response: Optional[str] = None
    customer_response_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True
