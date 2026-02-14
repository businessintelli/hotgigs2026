"""Pydantic schemas for candidate rediscovery models."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from schemas.common import BaseResponse


class CompetencyProfileCreate(BaseModel):
    """Create competency profile."""

    candidate_id: int = Field(gt=0)


class CompetencyProfileUpdate(BaseModel):
    """Update competency profile."""

    technical_proficiency: Optional[float] = Field(None, ge=0.0, le=5.0)
    communication: Optional[float] = Field(None, ge=0.0, le=5.0)
    problem_solving: Optional[float] = Field(None, ge=0.0, le=5.0)
    leadership: Optional[float] = Field(None, ge=0.0, le=5.0)
    culture_fit: Optional[float] = Field(None, ge=0.0, le=5.0)
    domain_expertise: Optional[float] = Field(None, ge=0.0, le=5.0)
    adaptability: Optional[float] = Field(None, ge=0.0, le=5.0)


class CompetencyProfileResponse(BaseResponse):
    """Competency profile response."""

    candidate_id: int
    technical_proficiency: Optional[float] = None
    communication: Optional[float] = None
    problem_solving: Optional[float] = None
    leadership: Optional[float] = None
    culture_fit: Optional[float] = None
    domain_expertise: Optional[float] = None
    adaptability: Optional[float] = None
    competency_details: Dict[str, Any]
    assessment_count: int
    last_assessed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CandidateRediscoveryCreate(BaseModel):
    """Create candidate rediscovery record."""

    candidate_id: int = Field(gt=0)
    requirement_id: int = Field(gt=0)
    original_requirement_id: Optional[int] = None


class CandidateRediscoveryUpdate(BaseModel):
    """Update candidate rediscovery record."""

    status: Optional[str] = Field(
        None,
        pattern="^(identified|contacted|responded|resubmitted|rejected)$",
    )
    response: Optional[str] = None
    notes: Optional[str] = None


class CandidateRediscoveryResponse(BaseResponse):
    """Candidate rediscovery response."""

    candidate_id: int
    requirement_id: int
    original_requirement_id: Optional[int] = None
    rediscovery_score: float
    skill_match_score: float
    interview_history_score: float
    recency_score: float
    engagement_score: float
    score_breakdown: Dict[str, Any]
    status: str
    contacted_at: Optional[datetime] = None
    response: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class RediscoveryCandidateListResponse(BaseModel):
    """List of rediscovery candidates with ranking."""

    candidate_id: int
    candidate_name: str
    email: str
    current_title: Optional[str] = None
    current_company: Optional[str] = None
    rediscovery_score: float
    skill_match_score: float
    interview_history_score: float
    recency_score: float
    engagement_score: float
    last_contacted_at: Optional[datetime] = None


class RediscoveryAnalyticsResponse(BaseModel):
    """Rediscovery analytics response."""

    total_talent_pool_size: int
    high_potential_candidates: int
    avg_time_in_talent_pool_days: float
    re_engagement_success_rate: float
    avg_rediscovery_score: float
    candidates_by_status: Dict[str, int]
    top_skills_in_pool: List[str]
    candidates_contacted_this_period: int
