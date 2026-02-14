"""Pydantic schemas for job post models."""

from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from schemas.common import BaseResponse


class JobPostCreate(BaseModel):
    """Create job post."""

    requirement_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    responsibilities: Optional[List[str]] = Field(default_factory=list)
    qualifications_required: Optional[List[str]] = Field(default_factory=list)
    qualifications_preferred: Optional[List[str]] = Field(default_factory=list)
    benefits: Optional[List[str]] = Field(default_factory=list)
    salary_range_min: Optional[float] = Field(None, ge=0)
    salary_range_max: Optional[float] = Field(None, ge=0)


class JobPostUpdate(BaseModel):
    """Update job post."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    summary: Optional[str] = None
    responsibilities: Optional[List[str]] = None
    qualifications_required: Optional[List[str]] = None
    qualifications_preferred: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    salary_range_min: Optional[float] = Field(None, ge=0)
    salary_range_max: Optional[float] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern="^(draft|published|archived)$")


class JobPostResponse(BaseResponse):
    """Job post response."""

    requirement_id: int
    title: str
    content: str
    summary: str
    responsibilities: List[str]
    qualifications_required: List[str]
    qualifications_preferred: List[str]
    benefits: List[str]
    salary_range_min: Optional[float] = None
    salary_range_max: Optional[float] = None
    seo_score: Optional[float] = None
    inclusivity_score: Optional[float] = None
    status: str
    published_at: Optional[datetime] = None
    published_boards: List[str]
    version: int
    created_by: Optional[int] = None

    class Config:
        from_attributes = True


class JobPostGenerateRequest(BaseModel):
    """Request to generate job post from requirement."""

    requirement_id: int = Field(gt=0)
    style: Optional[str] = Field(default="professional", pattern="^(professional|casual|technical)$")


class JobPostAnalyticsResponse(BaseResponse):
    """Job post analytics response."""

    job_post_id: int
    board_name: str
    views: int
    clicks: int
    applications: int
    period_start: date
    period_end: date

    class Config:
        from_attributes = True


class SEOOptimizationResponse(BaseModel):
    """SEO optimization result."""

    seo_score: float = Field(ge=0.0, le=100.0)
    keyword_density: Dict[str, float]
    title_suggestions: List[str]
    structured_data_suggestions: List[str]
    improvements: List[str]


class InclusivityCheckResponse(BaseModel):
    """Inclusivity language check result."""

    inclusivity_score: float = Field(ge=0.0, le=100.0)
    issues: List[Dict[str, Any]]  # {text, issue_type, severity, suggestion}
    gendered_words: List[str]
    age_bias_indicators: List[str]
    ability_bias_indicators: List[str]
    recommendations: List[str]


class SalaryRangeSuggestionResponse(BaseModel):
    """Salary range suggestion."""

    suggested_min: float
    suggested_max: float
    currency: str = "USD"
    rate_type: str
    market_data_points: int
    confidence_level: float
    comparable_roles: List[str]
    location: Optional[str] = None
    experience_level: Optional[str] = None


class JobPostVersionResponse(BaseModel):
    """Job post version for multi-board publishing."""

    board_name: str
    title: str
    content: str
    summary: str
    responsibilities: List[str]
    qualifications_required: List[str]
    benefits: List[str]
    format_notes: Optional[str] = None


class JobPostGenerateFromTextRequest(BaseModel):
    """Generate job post from freeform text."""

    freeform_text: str = Field(min_length=1)
    style: Optional[str] = Field(default="professional", pattern="^(professional|casual|technical)$")


class MultiboardPublishRequest(BaseModel):
    """Request to publish to multiple job boards."""

    job_post_id: int = Field(gt=0)
    boards: List[str] = Field(min_items=1)  # linkedin, indeed, company_career_page, etc
