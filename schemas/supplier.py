from pydantic import BaseModel, Field, EmailStr
from datetime import date, datetime
from typing import Optional, List
from models.enums import SupplierTier
from schemas.common import BaseResponse


class SupplierCreate(BaseModel):
    """Supplier creation schema."""

    company_name: str = Field(min_length=1, max_length=255)
    contact_name: Optional[str] = Field(default=None, max_length=255)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(default=None, max_length=20)
    website: Optional[str] = Field(default=None, max_length=255)
    specializations: Optional[List[str]] = Field(default_factory=list)
    locations_served: Optional[List[str]] = Field(default_factory=list)
    tier: Optional[SupplierTier] = Field(default=SupplierTier.NEW)
    commission_rate: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    contract_start: Optional[date] = None
    contract_end: Optional[date] = None
    notes: Optional[str] = None


class SupplierUpdate(BaseModel):
    """Supplier update schema."""

    company_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    contact_name: Optional[str] = Field(default=None, max_length=255)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(default=None, max_length=20)
    website: Optional[str] = Field(default=None, max_length=255)
    specializations: Optional[List[str]] = None
    locations_served: Optional[List[str]] = None
    tier: Optional[SupplierTier] = None
    commission_rate: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    contract_start: Optional[date] = None
    contract_end: Optional[date] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class SupplierResponse(BaseResponse):
    """Supplier response schema."""

    company_name: str
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    specializations: Optional[List[str]] = None
    locations_served: Optional[List[str]] = None
    tier: SupplierTier
    commission_rate: Optional[float] = None
    contract_start: Optional[date] = None
    contract_end: Optional[date] = None
    total_submissions: int
    total_placements: int
    avg_time_to_submit: Optional[float] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class SupplierPerformanceResponse(BaseResponse):
    """Supplier performance response schema."""

    supplier_id: int
    period_start: date
    period_end: date
    submissions_count: int
    placements_count: int
    rejection_rate: Optional[float] = None
    avg_match_score: Optional[float] = None
    avg_time_to_fill: Optional[float] = None
    quality_score: Optional[float] = None
    responsiveness_score: Optional[float] = None
    overall_rating: Optional[float] = None

    class Config:
        from_attributes = True
