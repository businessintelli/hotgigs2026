"""Pydantic schemas for resume harvesting."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class HarvestSourceCreate(BaseModel):
    """Create harvest source request."""

    name: str = Field(..., min_length=1, max_length=100)
    source_type: str = Field(..., description="job_board/social/developer_community/forum")
    api_endpoint: Optional[str] = Field(None, max_length=500)
    api_key_encrypted: Optional[str] = Field(None, max_length=500)
    api_secret_encrypted: Optional[str] = Field(None, max_length=500)
    rate_limit_per_hour: int = Field(default=100, ge=1)
    rate_limit_per_day: int = Field(default=1000, ge=1)
    config: Dict[str, Any] = Field(default_factory=dict)


class HarvestSourceUpdate(BaseModel):
    """Update harvest source request."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    api_key_encrypted: Optional[str] = Field(None, max_length=500)
    api_secret_encrypted: Optional[str] = Field(None, max_length=500)
    rate_limit_per_hour: Optional[int] = Field(None, ge=1)
    rate_limit_per_day: Optional[int] = Field(None, ge=1)
    config: Optional[Dict[str, Any]] = None


class HarvestSourceResponse(BaseModel):
    """Harvest source response."""

    id: int
    name: str
    source_type: str
    api_endpoint: Optional[str]
    rate_limit_per_hour: int
    rate_limit_per_day: int
    is_active: bool
    last_harvested_at: Optional[datetime]
    total_candidates_harvested: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HarvestJobCreate(BaseModel):
    """Create harvest job request."""

    source_id: int = Field(..., gt=0)
    search_criteria: Dict[str, Any] = Field(..., description="Search criteria: skills, location, experience, keywords")
    frequency: Optional[str] = Field(None, description="once/daily/weekly/monthly")


class HarvestJobResponse(BaseModel):
    """Harvest job response."""

    id: int
    source_id: int
    search_criteria: Dict[str, Any]
    frequency: Optional[str]
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    candidates_found: int
    candidates_new: int
    candidates_updated: int
    candidates_duplicate: int
    error_message: Optional[str]
    next_run_at: Optional[datetime]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HarvestResultResponse(BaseModel):
    """Harvest result response."""

    id: int
    job_id: int
    source_id: int
    candidate_id: Optional[int]
    raw_data: Dict[str, Any]
    source_profile_url: Optional[str]
    source_profile_id: Optional[str]
    status: str
    match_confidence: Optional[float]
    processed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CandidateSourceMappingResponse(BaseModel):
    """Candidate source mapping response."""

    id: int
    candidate_id: int
    source_id: int
    source_profile_id: str
    source_profile_url: Optional[str]
    source_data: Optional[Dict[str, Any]]
    last_synced_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HarvestSearchRequest(BaseModel):
    """Search candidates on a source."""

    source_name: str = Field(..., description="linkedin/dice/monster/indeed/github/stackoverflow/forums")
    search_criteria: Dict[str, Any] = Field(..., description="Keywords, skills, location, experience level")


class HarvestSearchResponse(BaseModel):
    """Harvest search response."""

    candidates: List[Dict[str, Any]] = Field(description="List of found candidates")
    total_count: int = Field(description="Total candidates found")
    source_name: str


class HarvestAnalyticsResponse(BaseModel):
    """Harvest analytics response."""

    total_sources: int
    active_sources: int
    total_candidates_harvested: int
    total_new_candidates: int
    candidates_by_source: Dict[str, int]
    harvest_jobs_total: int
    harvest_jobs_completed: int
    average_candidates_per_job: float
    cost_per_candidate: Optional[float]
    quality_scores: Dict[str, float]
