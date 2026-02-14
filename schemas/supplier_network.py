"""Pydantic schemas for supplier network models."""

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, date
from typing import Optional, List
from schemas.common import BaseResponse


class SupplierRequirementCreate(BaseModel):
    """Create supplier requirement distribution."""

    supplier_id: int = Field(gt=0)
    requirement_id: int = Field(gt=0)
    notes: Optional[str] = None


class SupplierRequirementUpdate(BaseModel):
    """Update supplier requirement."""

    response_status: Optional[str] = Field(None, pattern="^(pending|accepted|declined|submitted)$")
    candidates_submitted: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class SupplierRequirementResponse(BaseResponse):
    """Supplier requirement response."""

    supplier_id: int
    requirement_id: int
    distributed_at: datetime
    response_status: str
    responded_at: Optional[datetime] = None
    candidates_submitted: int
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class SupplierRateCardCreate(BaseModel):
    """Create supplier rate card."""

    supplier_id: int = Field(gt=0)
    role_title: str = Field(min_length=1, max_length=255)
    skill_category: str = Field(min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=255)
    min_rate: float = Field(gt=0)
    max_rate: float = Field(gt=0)
    rate_type: str = Field(pattern="^(hourly|annual|contract)$")
    effective_date: date
    expiry_date: Optional[date] = None
    notes: Optional[str] = None


class SupplierRateCardUpdate(BaseModel):
    """Update supplier rate card."""

    role_title: Optional[str] = Field(None, min_length=1, max_length=255)
    skill_category: Optional[str] = Field(None, min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=255)
    min_rate: Optional[float] = Field(None, gt=0)
    max_rate: Optional[float] = Field(None, gt=0)
    rate_type: Optional[str] = Field(None, pattern="^(hourly|annual|contract)$")
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    notes: Optional[str] = None


class SupplierRateCardResponse(BaseResponse):
    """Supplier rate card response."""

    supplier_id: int
    role_title: str
    skill_category: str
    location: Optional[str] = None
    min_rate: float
    max_rate: float
    rate_type: str
    effective_date: date
    expiry_date: Optional[date] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class SupplierCommunicationCreate(BaseModel):
    """Create supplier communication record."""

    supplier_id: int = Field(gt=0)
    communication_type: str = Field(
        pattern="^(requirement_distribution|follow_up|performance_review|general)$"
    )
    subject: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)


class SupplierCommunicationResponse(BaseResponse):
    """Supplier communication response."""

    supplier_id: int
    communication_type: str
    subject: str
    content: str
    sent_at: datetime
    sent_by: Optional[int] = None
    response: Optional[str] = None
    responded_at: Optional[datetime] = None

    class Config:
        from_attributes = True
