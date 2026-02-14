from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List
from models.enums import RequirementStatus, Priority
from schemas.common import BaseResponse


class RequirementCreate(BaseModel):
    """Requirement creation schema."""

    customer_id: int
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    skills_required: Optional[List[str]] = Field(default_factory=list)
    skills_preferred: Optional[List[str]] = Field(default_factory=list)
    experience_min: Optional[float] = Field(default=None, ge=0)
    experience_max: Optional[float] = Field(default=None, ge=0)
    education_level: Optional[str] = Field(default=None, max_length=100)
    certifications: Optional[List[str]] = Field(default_factory=list)
    employment_type: Optional[str] = Field(default=None, max_length=50)
    work_mode: Optional[str] = Field(default=None, max_length=50)
    location_city: Optional[str] = Field(default=None, max_length=100)
    location_state: Optional[str] = Field(default=None, max_length=100)
    location_country: Optional[str] = Field(default=None, max_length=100)
    rate_min: Optional[float] = Field(default=None, ge=0)
    rate_max: Optional[float] = Field(default=None, ge=0)
    rate_type: Optional[str] = Field(default=None, max_length=50)
    duration_months: Optional[int] = Field(default=None, ge=1)
    positions_count: int = Field(default=1, ge=1)
    priority: Optional[Priority] = Field(default=Priority.MEDIUM)
    assigned_recruiter_id: Optional[int] = None
    submission_deadline: Optional[date] = None
    start_date: Optional[date] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = Field(default_factory=dict)


class RequirementUpdate(BaseModel):
    """Requirement update schema."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    skills_required: Optional[List[str]] = None
    skills_preferred: Optional[List[str]] = None
    experience_min: Optional[float] = Field(default=None, ge=0)
    experience_max: Optional[float] = Field(default=None, ge=0)
    education_level: Optional[str] = Field(default=None, max_length=100)
    certifications: Optional[List[str]] = None
    employment_type: Optional[str] = Field(default=None, max_length=50)
    work_mode: Optional[str] = Field(default=None, max_length=50)
    location_city: Optional[str] = Field(default=None, max_length=100)
    location_state: Optional[str] = Field(default=None, max_length=100)
    location_country: Optional[str] = Field(default=None, max_length=100)
    rate_min: Optional[float] = Field(default=None, ge=0)
    rate_max: Optional[float] = Field(default=None, ge=0)
    rate_type: Optional[str] = Field(default=None, max_length=50)
    duration_months: Optional[int] = Field(default=None, ge=1)
    positions_count: Optional[int] = Field(default=None, ge=1)
    positions_filled: Optional[int] = Field(default=None, ge=0)
    priority: Optional[Priority] = None
    status: Optional[RequirementStatus] = None
    assigned_recruiter_id: Optional[int] = None
    submission_deadline: Optional[date] = None
    start_date: Optional[date] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = None
    is_active: Optional[bool] = None


class RequirementResponse(BaseResponse):
    """Requirement response schema."""

    customer_id: int
    title: str
    description: Optional[str] = None
    skills_required: Optional[List[str]] = None
    skills_preferred: Optional[List[str]] = None
    experience_min: Optional[float] = None
    experience_max: Optional[float] = None
    education_level: Optional[str] = None
    certifications: Optional[List[str]] = None
    employment_type: Optional[str] = None
    work_mode: Optional[str] = None
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    location_country: Optional[str] = None
    rate_min: Optional[float] = None
    rate_max: Optional[float] = None
    rate_type: Optional[str] = None
    duration_months: Optional[int] = None
    positions_count: int
    positions_filled: int
    priority: Optional[Priority] = None
    status: RequirementStatus
    assigned_recruiter_id: Optional[int] = None
    submission_deadline: Optional[date] = None
    start_date: Optional[date] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True
