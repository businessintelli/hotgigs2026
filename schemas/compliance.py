"""Schemas for compliance endpoints."""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel


class ComplianceRequirementCreate(BaseModel):
    organization_id: Optional[int] = None
    requirement_type: str
    is_mandatory: bool = True
    description: Optional[str] = None
    certification_name: Optional[str] = None
    issuing_body: Optional[str] = None
    renewal_frequency_days: Optional[int] = None
    risk_level: str = "medium"


class ComplianceRequirementResponse(BaseModel):
    id: int
    organization_id: Optional[int]
    requirement_type: str
    is_mandatory: bool
    description: Optional[str]
    certification_name: Optional[str]
    issuing_body: Optional[str]
    renewal_frequency_days: Optional[int]
    risk_level: str
    created_at: datetime
    class Config:
        from_attributes = True


class ComplianceRecordCreate(BaseModel):
    placement_id: int
    candidate_id: int
    compliance_requirement_id: int
    required_by: Optional[date] = None
    provider_name: Optional[str] = None
    provider_reference_id: Optional[str] = None


class ComplianceRecordUpdate(BaseModel):
    status: Optional[str] = None
    verification_notes: Optional[str] = None
    passed: Optional[bool] = None
    risk_score: Optional[float] = None
    notes: Optional[str] = None


class ComplianceRecordResponse(BaseModel):
    id: int
    placement_id: int
    candidate_id: int
    compliance_requirement_id: int
    status: str
    required_by: Optional[date]
    completed_at: Optional[datetime]
    expires_at: Optional[datetime]
    verified_by: Optional[int]
    passed: Optional[bool]
    risk_score: Optional[float]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


class ComplianceScoreResponse(BaseModel):
    supplier_org_id: int
    overall_score: float
    completed_requirements: int
    total_requirements: int
    expired_requirements: int
    failed_requirements: int


class PlacementComplianceResponse(BaseModel):
    placement_id: int
    is_compliant: bool
    total: int
    completed: int
    expired: int
    failed: int
    gaps: List[int] = []
