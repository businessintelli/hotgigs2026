"""Organization and tenant management request/response schemas."""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, date


# --- Organization Schemas ---

class OrganizationCreate(BaseModel):
    """Create a new organization (client or supplier)."""
    name: str = Field(..., min_length=1, max_length=255)
    org_type: str = Field(..., pattern="^(msp|client|supplier)$")
    slug: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    primary_contact_name: Optional[str] = Field(None, max_length=200)
    primary_contact_email: Optional[EmailStr] = None
    primary_contact_phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=20)
    # Supplier-specific
    tier: Optional[str] = Field(None, pattern="^(platinum|gold|silver|bronze|new|standard)$")
    commission_rate: Optional[float] = Field(None, ge=0, le=100)
    specializations: Optional[List[str]] = None
    # Contract
    contract_start: Optional[date] = None
    contract_end: Optional[date] = None
    billing_rate_type: Optional[str] = Field(None, max_length=50)


class OrganizationUpdate(BaseModel):
    """Update an existing organization."""
    name: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    primary_contact_name: Optional[str] = Field(None, max_length=200)
    primary_contact_email: Optional[EmailStr] = None
    primary_contact_phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=20)
    tier: Optional[str] = Field(None, pattern="^(platinum|gold|silver|bronze|new|standard)$")
    commission_rate: Optional[float] = Field(None, ge=0, le=100)
    specializations: Optional[List[str]] = None
    contract_start: Optional[date] = None
    contract_end: Optional[date] = None
    billing_rate_type: Optional[str] = Field(None, max_length=50)
    settings: Optional[Dict[str, Any]] = None


class OrganizationResponse(BaseModel):
    """Organization response model."""
    id: int
    name: str
    slug: str
    org_type: str
    logo_url: Optional[str] = None
    onboarding_status: str
    parent_org_id: Optional[int] = None
    primary_contact_name: Optional[str] = None
    primary_contact_email: Optional[str] = None
    primary_contact_phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    tier: Optional[str] = None
    commission_rate: Optional[float] = None
    contract_start: Optional[date] = None
    contract_end: Optional[date] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class OrganizationListResponse(BaseModel):
    """Paginated list of organizations."""
    items: List[OrganizationResponse]
    total: int
    offset: int
    limit: int


# --- Membership Schemas ---

class MembershipResponse(BaseModel):
    """Organization membership response."""
    id: int
    organization_id: int
    user_id: int
    role: str
    is_primary: bool
    department: Optional[str] = None
    title: Optional[str] = None
    joined_at: datetime
    # Nested user info
    user_email: Optional[str] = None
    user_name: Optional[str] = None

    class Config:
        from_attributes = True


class InvitationCreate(BaseModel):
    """Create an invitation to join an organization."""
    email: EmailStr
    role: str = Field(..., pattern="^(msp_admin|msp_manager|msp_recruiter|client_admin|client_manager|client_viewer|supplier_admin|supplier_recruiter|supplier_viewer)$")
    message: Optional[str] = None


class InvitationResponse(BaseModel):
    """Invitation response."""
    id: int
    organization_id: int
    email: str
    role: str
    status: str
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# --- Org Switching ---

class SwitchOrgRequest(BaseModel):
    """Request to switch active organization."""
    organization_id: int


class SwitchOrgResponse(BaseModel):
    """Response after switching organization."""
    access_token: str
    organization: OrganizationResponse
    role: str
