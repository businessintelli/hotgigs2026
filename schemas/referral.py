from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class ReferrerCreateSchema(BaseModel):
    """Schema for registering as referrer."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=5, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    referrer_type: str = Field(..., min_length=1, max_length=50)
    company: Optional[str] = Field(None, max_length=255)
    specializations: List[str] = Field(default_factory=list)
    network_size_estimate: Optional[int] = Field(None, ge=0)


class ReferrerUpdateSchema(BaseModel):
    """Schema for updating referrer profile."""

    phone: Optional[str] = Field(None, max_length=20)
    specializations: Optional[List[str]] = None
    network_size_estimate: Optional[int] = Field(None, ge=0)
    payment_method: Optional[str] = Field(None, max_length=50)
    payment_details: Optional[Dict[str, Any]] = None


class ReferrerSchema(ReferrerCreateSchema):
    """Schema for referrer response."""

    id: int
    user_id: Optional[int] = None
    referral_code: str
    is_active: bool
    total_referrals: int
    successful_placements: int
    total_earnings: float
    pending_earnings: float
    payment_method: Optional[str] = None
    tier: str
    joined_at: datetime
    created_at: datetime
    updated_at: datetime


class ReferralCreateSchema(BaseModel):
    """Schema for creating a referral."""

    candidate_data: Dict[str, Any] = Field(...)
    requirement_id: Optional[int] = None
    relationship_to_candidate: Optional[str] = Field(None, max_length=100)
    referral_notes: Optional[str] = None


class ReferralUpdateSchema(BaseModel):
    """Schema for updating referral."""

    status: Optional[str] = None
    relationship_to_candidate: Optional[str] = None
    referral_notes: Optional[str] = None


class ReferralSchema(BaseModel):
    """Schema for referral response."""

    id: int
    referrer_id: int
    candidate_id: int
    requirement_id: Optional[int] = None
    referral_code_used: str
    referral_link: Optional[str] = None
    relationship_to_candidate: Optional[str] = None
    referral_notes: Optional[str] = None
    status: str
    is_hidden_role: bool
    current_milestone: str
    submitted_at: datetime
    last_milestone_at: Optional[datetime] = None
    placed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ReferralMilestoneSchema(BaseModel):
    """Schema for recording referral milestone."""

    milestone: str = Field(..., min_length=1)
    details: Optional[Dict[str, Any]] = None


class ReferralBonusCreateSchema(BaseModel):
    """Schema for creating referral bonus."""

    referral_id: int
    milestone: str = Field(..., min_length=1)
    bonus_amount: float = Field(..., gt=0)
    bonus_currency: str = Field(default="USD", max_length=3)


class ReferralBonusSchema(BaseModel):
    """Schema for referral bonus response."""

    id: int
    referral_id: int
    referrer_id: int
    milestone: str
    bonus_amount: float
    bonus_currency: str
    status: str
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    payment_reference: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ReferralBonusApproveSchema(BaseModel):
    """Schema for approving bonus."""

    notes: Optional[str] = None


class ReferralBonusPaySchema(BaseModel):
    """Schema for marking bonus as paid."""

    payment_reference: str = Field(..., min_length=1, max_length=255)
    notes: Optional[str] = None


class ReferralBonusConfigCreateSchema(BaseModel):
    """Schema for creating bonus configuration."""

    name: str = Field(..., min_length=1, max_length=255)
    requirement_id: Optional[int] = None
    customer_id: Optional[int] = None
    bonus_structure: Dict[str, float] = Field(...)
    max_bonus_per_referral: Optional[float] = Field(None, gt=0)
    is_default: bool = False


class ReferralBonusConfigSchema(ReferralBonusConfigCreateSchema):
    """Schema for bonus configuration response."""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ReferralDashboardSchema(BaseModel):
    """Schema for referrer dashboard."""

    referrer: ReferrerSchema
    total_referrals: int
    active_referrals: int
    placed_referrals: int
    rejected_referrals: int
    total_earnings: float
    pending_earnings: float
    recent_referrals: List[ReferralSchema]
    pending_bonuses: List[ReferralBonusSchema]
    hidden_roles_available: int
    tier_progress: Dict[str, Any]


class ReferralEarningsSchema(BaseModel):
    """Schema for referrer earnings."""

    referrer_id: int
    total_earnings: float
    pending_earnings: float
    paid_earnings: float
    earned_bonuses: List[ReferralBonusSchema]


class ReferralLeaderboardEntrySchema(BaseModel):
    """Schema for referral leaderboard entry."""

    referrer_id: int
    name: str
    referral_code: str
    tier: str
    total_referrals: int
    successful_placements: int
    total_earnings: float
    conversion_rate: float
    rank: int


class NetworkAnalyticsSchema(BaseModel):
    """Schema for referral network analytics."""

    total_referrers: int
    active_referrers: int
    total_referrals: int
    placed_referrals: int
    conversion_rate: float
    total_bonuses_paid: float
    avg_time_to_hire_days: float
    vs_non_referral_hiring: Dict[str, Any]
    referrals_by_tier: Dict[str, int]
    top_referrers: List[ReferralLeaderboardEntrySchema]
    bonuses_by_milestone: Dict[str, float]


class HiddenRoleOpportunitySchema(BaseModel):
    """Schema for hidden role available to referrers."""

    requirement_id: int
    title: str
    description: str
    rate_min: float
    rate_max: float
    location: Optional[str] = None
    specializations_required: List[str]
    bonus_amount: float
    bonus_structure: Dict[str, float]
    available_until: datetime
    referral_link: Optional[str] = None


class ReferralOpportunityPushSchema(BaseModel):
    """Schema for pushing opportunity to referrers."""

    requirement_id: int
    referrer_ids: List[int] = Field(default_factory=list)
    target_specializations: List[str] = Field(default_factory=list)
    message: Optional[str] = None


class ReferralLinkSchema(BaseModel):
    """Schema for referral link."""

    referral_link: str
    referral_code: str
    requirement_id: Optional[int] = None
    expires_at: Optional[datetime] = None
