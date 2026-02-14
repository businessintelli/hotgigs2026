from pydantic import BaseModel, Field, EmailStr
from datetime import date, datetime
from typing import Optional
from schemas.common import BaseResponse, TimestampMixin


class CustomerCreate(BaseModel):
    """Customer creation schema."""

    name: str = Field(min_length=1, max_length=255)
    industry: Optional[str] = Field(default=None, max_length=100)
    website: Optional[str] = Field(default=None, max_length=255)
    primary_contact_name: Optional[str] = Field(default=None, max_length=255)
    primary_contact_email: Optional[EmailStr] = None
    primary_contact_phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=255)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    country: Optional[str] = Field(default=None, max_length=100)
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    billing_rate_type: Optional[str] = Field(default=None, max_length=50)
    notes: Optional[str] = None
    metadata: Optional[dict] = Field(default_factory=dict)


class CustomerUpdate(BaseModel):
    """Customer update schema."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    industry: Optional[str] = Field(default=None, max_length=100)
    website: Optional[str] = Field(default=None, max_length=255)
    primary_contact_name: Optional[str] = Field(default=None, max_length=255)
    primary_contact_email: Optional[EmailStr] = None
    primary_contact_phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=255)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    country: Optional[str] = Field(default=None, max_length=100)
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    billing_rate_type: Optional[str] = Field(default=None, max_length=50)
    notes: Optional[str] = None
    metadata: Optional[dict] = None
    is_active: Optional[bool] = None


class CustomerResponse(BaseResponse):
    """Customer response schema."""

    name: str
    industry: Optional[str] = None
    website: Optional[str] = None
    primary_contact_name: Optional[str] = None
    primary_contact_email: Optional[str] = None
    primary_contact_phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    billing_rate_type: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True
