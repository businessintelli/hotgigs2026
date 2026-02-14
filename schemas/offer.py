from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List
from models.enums import OfferStatus, OnboardingStatus
from schemas.common import BaseResponse


class OfferCreate(BaseModel):
    """Offer creation schema."""

    submission_id: int
    candidate_id: int
    requirement_id: int
    offered_rate: Optional[float] = Field(default=None, ge=0)
    rate_type: Optional[str] = Field(default=None, max_length=50)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None


class OfferUpdate(BaseModel):
    """Offer update schema."""

    offered_rate: Optional[float] = Field(default=None, ge=0)
    rate_type: Optional[str] = Field(default=None, max_length=50)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[OfferStatus] = None
    offer_letter_path: Optional[str] = Field(default=None, max_length=500)
    response_at: Optional[datetime] = None
    negotiation_history: Optional[List[dict]] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class OfferResponse(BaseResponse):
    """Offer response schema."""

    submission_id: int
    candidate_id: int
    requirement_id: int
    offered_rate: Optional[float] = None
    rate_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: OfferStatus
    offer_letter_path: Optional[str] = None
    sent_at: Optional[datetime] = None
    response_at: Optional[datetime] = None
    negotiation_history: Optional[List[dict]] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class ChecklistItemModel(BaseModel):
    """Onboarding checklist item model."""

    item: str
    completed: bool = False
    completed_at: Optional[datetime] = None


class OnboardingCreate(BaseModel):
    """Onboarding creation schema."""

    offer_id: int
    candidate_id: int
    checklist: Optional[List[ChecklistItemModel]] = Field(default_factory=list)
    documents_collected: Optional[List[str]] = Field(default_factory=list)
    background_check_status: Optional[str] = Field(default=None, max_length=100)
    start_date_confirmed: Optional[date] = None
    notes: Optional[str] = None


class OnboardingUpdate(BaseModel):
    """Onboarding update schema."""

    status: Optional[OnboardingStatus] = None
    checklist: Optional[List[ChecklistItemModel]] = None
    documents_collected: Optional[List[str]] = None
    background_check_status: Optional[str] = Field(default=None, max_length=100)
    start_date_confirmed: Optional[date] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class OnboardingResponse(BaseResponse):
    """Onboarding response schema."""

    offer_id: int
    candidate_id: int
    status: OnboardingStatus
    checklist: Optional[List[ChecklistItemModel]] = None
    documents_collected: Optional[List[str]] = None
    background_check_status: Optional[str] = None
    start_date_confirmed: Optional[date] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True
