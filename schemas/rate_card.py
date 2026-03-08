"""Schemas for rate card endpoints."""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class RateCardEntryCreate(BaseModel):
    skill_name: str
    skill_level: str
    bill_rate: Optional[float] = None
    pay_rate: Optional[float] = None


class RateCardEntryResponse(BaseModel):
    id: int
    rate_card_id: int
    skill_name: str
    skill_level: str
    bill_rate: Optional[float]
    pay_rate: Optional[float]
    class Config:
        from_attributes = True


class RateCardCreate(BaseModel):
    client_org_id: int
    job_category: str
    location: Optional[str] = None
    skill_level: Optional[str] = None
    bill_rate_min: float = Field(gt=0)
    bill_rate_max: float = Field(gt=0)
    pay_rate_min: float = Field(gt=0)
    pay_rate_max: float = Field(gt=0)
    overtime_multiplier: float = Field(default=1.5, gt=0)
    weekend_multiplier: Optional[float] = Field(default=1.25)
    shift_premium: Optional[float] = Field(default=0.0)
    currency: str = "USD"
    effective_from: date
    effective_to: Optional[date] = None
    notes: Optional[str] = None
    entries: List[RateCardEntryCreate] = []

    @field_validator("bill_rate_max")
    @classmethod
    def validate_bill_max(cls, v, info):
        if "bill_rate_min" in info.data and v < info.data["bill_rate_min"]:
            raise ValueError("bill_rate_max must be >= bill_rate_min")
        return v

    @field_validator("pay_rate_max")
    @classmethod
    def validate_pay_max(cls, v, info):
        if "pay_rate_min" in info.data and v < info.data["pay_rate_min"]:
            raise ValueError("pay_rate_max must be >= pay_rate_min")
        return v


class RateCardUpdate(BaseModel):
    job_category: Optional[str] = None
    location: Optional[str] = None
    bill_rate_min: Optional[float] = None
    bill_rate_max: Optional[float] = None
    pay_rate_min: Optional[float] = None
    pay_rate_max: Optional[float] = None
    overtime_multiplier: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class RateCardResponse(BaseModel):
    id: int
    client_org_id: int
    job_category: str
    location: Optional[str]
    skill_level: Optional[str]
    bill_rate_min: float
    bill_rate_max: float
    pay_rate_min: float
    pay_rate_max: float
    overtime_multiplier: float
    weekend_multiplier: Optional[float]
    shift_premium: Optional[float]
    currency: str
    effective_from: date
    effective_to: Optional[date]
    status: str
    notes: Optional[str]
    entries: List[RateCardEntryResponse] = []
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


class RateValidationRequest(BaseModel):
    client_org_id: int
    job_category: str
    bill_rate: float
    pay_rate: float
    location: Optional[str] = None


class RateValidationResponse(BaseModel):
    is_valid: bool
    rate_card_id: Optional[int] = None
    violations: List[dict] = []
    message: str = ""
