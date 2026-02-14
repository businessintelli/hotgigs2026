from pydantic import BaseModel, Field, field_validator, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime, date


class CandidateProfileCreateSchema(BaseModel):
    """Schema for creating candidate profile."""

    headline: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=5000)
    portfolio_url: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    personal_website: Optional[str] = None

    # Preferences
    desired_roles: List[str] = Field(default_factory=list)
    desired_locations: List[str] = Field(default_factory=list)
    desired_rate_min: Optional[float] = Field(None, ge=0)
    desired_rate_max: Optional[float] = Field(None, ge=0)
    rate_type: Optional[str] = None

    # Availability
    availability_date: Optional[date] = None
    availability_status: str = Field(default="not_looking")
    work_preferences: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("desired_rate_max")
    @classmethod
    def validate_rates(cls, v: Optional[float], info) -> Optional[float]:
        if v is not None and info.data.get("desired_rate_min") is not None:
            if v < info.data["desired_rate_min"]:
                raise ValueError("Max rate must be >= min rate")
        return v


class CandidateProfileUpdateSchema(BaseModel):
    """Schema for updating candidate profile."""

    headline: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=5000)
    portfolio_url: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    personal_website: Optional[str] = None
    desired_roles: Optional[List[str]] = None
    desired_locations: Optional[List[str]] = None
    desired_rate_min: Optional[float] = Field(None, ge=0)
    desired_rate_max: Optional[float] = Field(None, ge=0)
    rate_type: Optional[str] = None
    availability_date: Optional[date] = None
    availability_status: Optional[str] = None
    work_preferences: Optional[Dict[str, Any]] = None


class CandidateProfileSchema(CandidateProfileCreateSchema):
    """Schema for candidate profile response."""

    id: int
    candidate_id: int
    ai_enhanced_bio: Optional[str] = None
    profile_completeness: float
    is_public: bool
    last_active_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ExperienceEntrySchema(BaseModel):
    """Schema for experience entry in resume."""

    company: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    description: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)


class EducationEntrySchema(BaseModel):
    """Schema for education entry in resume."""

    institution: str = Field(..., min_length=1)
    degree: str = Field(..., min_length=1)
    field: str = Field(..., min_length=1)
    start_date: date
    end_date: Optional[date] = None
    gpa: Optional[float] = Field(None, ge=0, le=4.0)


class SkillEntrySchema(BaseModel):
    """Schema for skill in resume."""

    name: str = Field(..., min_length=1)
    level: Optional[str] = None


class CertificationEntrySchema(BaseModel):
    """Schema for certification in resume."""

    name: str = Field(..., min_length=1)
    issuer: Optional[str] = None
    issue_date: Optional[date] = None
    expiration_date: Optional[date] = None


class ProjectEntrySchema(BaseModel):
    """Schema for project in resume."""

    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    url: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)


class ResumeBuilderDataCreateSchema(BaseModel):
    """Schema for creating resume builder data."""

    template_name: str = Field(default="professional", min_length=1)
    personal_info: Dict[str, Any] = Field(default_factory=dict)
    summary: Optional[str] = None
    experience: List[ExperienceEntrySchema] = Field(default_factory=list)
    education: List[EducationEntrySchema] = Field(default_factory=list)
    skills: Dict[str, List[SkillEntrySchema]] = Field(default_factory=dict)
    certifications: List[CertificationEntrySchema] = Field(default_factory=list)
    projects: List[ProjectEntrySchema] = Field(default_factory=list)
    languages: List[Dict[str, Any]] = Field(default_factory=list)
    custom_sections: List[Dict[str, Any]] = Field(default_factory=list)


class ResumeBuilderDataUpdateSchema(BaseModel):
    """Schema for updating resume builder data."""

    template_name: Optional[str] = None
    personal_info: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    experience: Optional[List[ExperienceEntrySchema]] = None
    education: Optional[List[EducationEntrySchema]] = None
    skills: Optional[Dict[str, List[SkillEntrySchema]]] = None
    certifications: Optional[List[CertificationEntrySchema]] = None
    projects: Optional[List[ProjectEntrySchema]] = None
    languages: Optional[List[Dict[str, Any]]] = None
    custom_sections: Optional[List[Dict[str, Any]]] = None


class ResumeEnhancementSchema(BaseModel):
    """Schema for resume section enhancement."""

    section_type: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    target_role: Optional[str] = None


class ResumeBuilderDataSchema(ResumeBuilderDataCreateSchema):
    """Schema for resume builder data response."""

    id: int
    candidate_id: int
    ai_enhanced_summary: Optional[str] = None
    generated_pdf_path: Optional[str] = None
    generated_docx_path: Optional[str] = None
    last_generated_at: Optional[datetime] = None
    version: int
    created_at: datetime
    updated_at: datetime


class CandidateVideoCreateSchema(BaseModel):
    """Schema for uploading candidate video."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    video_type: str = Field(..., min_length=1, max_length=50)


class CandidateVideoSchema(BaseModel):
    """Schema for candidate video response."""

    id: int
    candidate_id: int
    title: str
    description: Optional[str] = None
    video_url: str
    thumbnail_url: Optional[str] = None
    duration_seconds: int
    video_type: str
    transcript: Optional[str] = None
    ai_summary: Optional[str] = None
    skills_mentioned: List[str]
    is_active: bool
    view_count: int
    uploaded_at: datetime
    created_at: datetime
    updated_at: datetime


class SubmissionPackageSchema(BaseModel):
    """Schema for candidate submission package."""

    candidate_id: int
    requirement_id: int
    profile: CandidateProfileSchema
    resume: Optional[ResumeBuilderDataSchema] = None
    videos: List[CandidateVideoSchema] = Field(default_factory=list)
    match_score: float
    created_at: datetime


class CandidatePortalDashboardSchema(BaseModel):
    """Schema for candidate portal dashboard."""

    profile: CandidateProfileSchema
    resumes: List[ResumeBuilderDataSchema]
    videos: List[CandidateVideoSchema]
    applications_count: int
    pending_interviews_count: int
    pending_offers_count: int
    latest_applications: List[Dict[str, Any]]
    upcoming_interviews: List[Dict[str, Any]]
    profile_completeness: float


class AvailabilityUpdateSchema(BaseModel):
    """Schema for updating availability."""

    availability_date: Optional[date] = None
    availability_status: str = Field(default="not_looking")
    desired_rate_min: Optional[float] = Field(None, ge=0)
    desired_rate_max: Optional[float] = Field(None, ge=0)
    rate_type: Optional[str] = None
    work_preferences: Optional[Dict[str, Any]] = None
