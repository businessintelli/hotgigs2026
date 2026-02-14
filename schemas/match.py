from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from models.enums import MatchStatus
from schemas.common import BaseResponse


class MatchScoreCreate(BaseModel):
    """Match score creation schema."""

    requirement_id: int
    candidate_id: int
    overall_score: float = Field(ge=0.0, le=100.0)
    skill_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    experience_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    education_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    location_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    rate_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    availability_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    culture_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    score_breakdown: Optional[dict] = Field(default_factory=dict)
    missing_skills: Optional[List[str]] = Field(default_factory=list)
    standout_qualities: Optional[List[str]] = Field(default_factory=list)
    matched_by: Optional[str] = Field(default="system", max_length=50)
    notes: Optional[str] = None


class MatchScoreUpdate(BaseModel):
    """Match score update schema."""

    overall_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    skill_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    experience_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    education_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    location_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    rate_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    availability_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    culture_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    status: Optional[MatchStatus] = None
    missing_skills: Optional[List[str]] = None
    standout_qualities: Optional[List[str]] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class MatchScoreResponse(BaseResponse):
    """Match score response schema."""

    requirement_id: int
    candidate_id: int
    overall_score: float
    skill_score: Optional[float] = None
    experience_score: Optional[float] = None
    education_score: Optional[float] = None
    location_score: Optional[float] = None
    rate_score: Optional[float] = None
    availability_score: Optional[float] = None
    culture_score: Optional[float] = None
    score_breakdown: Optional[dict] = None
    missing_skills: Optional[List[str]] = None
    standout_qualities: Optional[List[str]] = None
    status: MatchStatus
    matched_at: datetime
    matched_by: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True
