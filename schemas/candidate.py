from pydantic import BaseModel, Field, EmailStr
from datetime import date, datetime
from typing import Optional, List
from models.enums import CandidateStatus
from schemas.common import BaseResponse


class SkillModel(BaseModel):
    """Candidate skill model."""

    skill: str
    level: Optional[str] = None
    years: Optional[float] = None


class EducationModel(BaseModel):
    """Candidate education model."""

    degree: str
    field: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[int] = None


class CandidateCreate(BaseModel):
    """Candidate creation schema."""

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=20)
    linkedin_url: Optional[str] = Field(default=None, max_length=500)
    location_city: Optional[str] = Field(default=None, max_length=100)
    location_state: Optional[str] = Field(default=None, max_length=100)
    location_country: Optional[str] = Field(default=None, max_length=100)
    current_title: Optional[str] = Field(default=None, max_length=255)
    current_company: Optional[str] = Field(default=None, max_length=255)
    total_experience_years: Optional[float] = Field(default=None, ge=0)
    skills: Optional[List[SkillModel]] = Field(default_factory=list)
    education: Optional[List[EducationModel]] = Field(default_factory=list)
    certifications: Optional[List[str]] = Field(default_factory=list)
    desired_rate: Optional[float] = Field(default=None, ge=0)
    desired_rate_type: Optional[str] = Field(default=None, max_length=50)
    availability_date: Optional[date] = None
    work_authorization: Optional[str] = Field(default=None, max_length=100)
    willing_to_relocate: Optional[bool] = Field(default=False)
    source: Optional[str] = Field(default=None, max_length=100)
    source_detail: Optional[str] = Field(default=None, max_length=500)
    supplier_id: Optional[int] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = Field(default_factory=dict)


class CandidateUpdate(BaseModel):
    """Candidate update schema."""

    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    linkedin_url: Optional[str] = Field(default=None, max_length=500)
    location_city: Optional[str] = Field(default=None, max_length=100)
    location_state: Optional[str] = Field(default=None, max_length=100)
    location_country: Optional[str] = Field(default=None, max_length=100)
    current_title: Optional[str] = Field(default=None, max_length=255)
    current_company: Optional[str] = Field(default=None, max_length=255)
    total_experience_years: Optional[float] = Field(default=None, ge=0)
    skills: Optional[List[SkillModel]] = None
    education: Optional[List[EducationModel]] = None
    certifications: Optional[List[str]] = None
    desired_rate: Optional[float] = Field(default=None, ge=0)
    desired_rate_type: Optional[str] = Field(default=None, max_length=50)
    availability_date: Optional[date] = None
    work_authorization: Optional[str] = Field(default=None, max_length=100)
    willing_to_relocate: Optional[bool] = None
    status: Optional[CandidateStatus] = None
    source: Optional[str] = Field(default=None, max_length=100)
    source_detail: Optional[str] = Field(default=None, max_length=500)
    supplier_id: Optional[int] = None
    notes: Optional[str] = None
    engagement_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    last_contacted_at: Optional[date] = None
    metadata: Optional[dict] = None
    is_active: Optional[bool] = None


class CandidateResponse(BaseResponse):
    """Candidate response schema."""

    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    location_country: Optional[str] = None
    current_title: Optional[str] = None
    current_company: Optional[str] = None
    total_experience_years: Optional[float] = None
    skills: Optional[List[SkillModel]] = None
    education: Optional[List[EducationModel]] = None
    certifications: Optional[List[str]] = None
    desired_rate: Optional[float] = None
    desired_rate_type: Optional[str] = None
    availability_date: Optional[date] = None
    work_authorization: Optional[str] = None
    willing_to_relocate: Optional[bool] = None
    status: CandidateStatus
    source: Optional[str] = None
    source_detail: Optional[str] = None
    supplier_id: Optional[int] = None
    notes: Optional[str] = None
    engagement_score: Optional[float] = None
    last_contacted_at: Optional[date] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True
