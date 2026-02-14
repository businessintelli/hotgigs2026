"""Pydantic schemas for digital marketing."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class MarketingCampaignCreate(BaseModel):
    """Create marketing campaign request."""

    name: str = Field(..., min_length=1, max_length=255)
    campaign_type: str = Field(..., description="job_promotion/bench_marketing/hotlist_blast/brand_awareness")
    requirement_ids: Optional[List[int]] = None
    candidate_ids: Optional[List[int]] = None
    hotlist_id: Optional[int] = None
    content: Dict[str, Any] = Field(..., description="Platform-specific content")
    target_audience: Optional[Dict[str, Any]] = None
    channels: List[str] = Field(..., description="linkedin/email/indeed/twitter/facebook")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget_total: Optional[float] = None


class MarketingCampaignUpdate(BaseModel):
    """Update marketing campaign request."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    target_audience: Optional[Dict[str, Any]] = None
    channels: Optional[List[str]] = None
    budget_total: Optional[float] = None


class MarketingCampaignResponse(BaseModel):
    """Marketing campaign response."""

    id: int
    name: str
    campaign_type: str
    status: str
    requirement_ids: Optional[List[int]]
    candidate_ids: Optional[List[int]]
    hotlist_id: Optional[int]
    channels: List[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    budget_total: Optional[float]
    budget_spent: float
    impressions: int
    clicks: int
    applications: int
    conversions: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HotlistCreate(BaseModel):
    """Create hotlist request."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    skill_category: str = Field(..., min_length=1, max_length=100)
    candidate_ids: List[int] = Field(default_factory=list)
    is_auto_updated: bool = Field(default=False)
    auto_update_criteria: Optional[Dict[str, Any]] = None
    shared_with: Optional[List[int]] = None


class HotlistUpdate(BaseModel):
    """Update hotlist request."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    candidate_ids: Optional[List[int]] = None
    is_auto_updated: Optional[bool] = None
    auto_update_criteria: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class HotlistResponse(BaseModel):
    """Hotlist response."""

    id: int
    name: str
    description: Optional[str]
    skill_category: str
    candidate_ids: List[int]
    is_auto_updated: bool
    auto_update_criteria: Optional[Dict[str, Any]]
    status: str
    shared_with: Optional[List[int]]
    last_sent_at: Optional[datetime]
    view_count: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CampaignDistributionResponse(BaseModel):
    """Campaign distribution response."""

    id: int
    campaign_id: int
    channel: str
    status: str
    distributed_at: Optional[datetime]
    impressions: int
    clicks: int
    applications: int
    cost: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmailCampaignTrackingResponse(BaseModel):
    """Email campaign tracking response."""

    id: int
    campaign_id: int
    recipient_email: str
    recipient_name: Optional[str]
    recipient_company: Optional[str]
    status: str
    sent_at: datetime
    opened_at: Optional[datetime]
    clicked_at: Optional[datetime]
    open_count: int
    click_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GenerateJobAdRequest(BaseModel):
    """Generate job advertisement request."""

    requirement_id: int = Field(..., gt=0)
    platform: str = Field(..., description="linkedin/indeed/twitter/facebook/google_jobs/email")


class GenerateJobAdResponse(BaseModel):
    """Generate job advertisement response."""

    title: str
    body: str
    platform: str
    keywords: List[str]
    call_to_action: str
    hashtags: Optional[List[str]] = None


class GenerateBenchProfileRequest(BaseModel):
    """Generate bench profile request."""

    candidate_id: int = Field(..., gt=0)


class GenerateBenchProfileResponse(BaseModel):
    """Generate bench profile response."""

    profile_title: str
    summary: str
    skills: List[str]
    availability: str
    experience_level: str


class GenerateSocialPostRequest(BaseModel):
    """Generate social media post request."""

    content_type: str = Field(..., description="job/candidate/hotlist")
    entity_id: int = Field(..., gt=0)
    platform: str = Field(..., description="linkedin/twitter/facebook")


class GenerateSocialPostResponse(BaseModel):
    """Generate social media post response."""

    post_text: str
    platform: str
    hashtags: List[str]
    media_recommendations: Optional[Dict[str, Any]] = None


class CampaignPerformanceResponse(BaseModel):
    """Campaign performance metrics."""

    campaign_id: int
    impressions: int
    clicks: int
    applications: int
    conversions: int
    click_through_rate: float
    conversion_rate: float
    cost_per_click: Optional[float]
    cost_per_application: Optional[float]
    budget_spent: float
    budget_remaining: Optional[float]


class MarketingAnalyticsResponse(BaseModel):
    """Marketing analytics response."""

    campaigns_active: int
    campaigns_completed: int
    total_reach: int
    total_impressions: int
    total_clicks: int
    total_applications: int
    average_ctr: float
    average_conversion_rate: float
    cost_per_application: Optional[float]
    best_performing_channel: str
    best_performing_campaign_type: str
    roi_by_campaign_type: Dict[str, float]
