from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date


class ContractPartySchema(BaseModel):
    """Schema for a party in a contract."""

    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., min_length=5, max_length=255)
    role: str = Field(..., min_length=1, max_length=100)
    entity_type: str = Field(..., min_length=1, max_length=100)
    entity_id: Optional[int] = None


class ContractTemplateCreateSchema(BaseModel):
    """Schema for creating a contract template."""

    name: str = Field(..., min_length=1, max_length=255)
    template_type: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)
    variables: Dict[str, Any] = Field(default_factory=dict)


class ContractTemplateSchema(ContractTemplateCreateSchema):
    """Schema for contract template response."""

    id: int
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ContractCreateSchema(BaseModel):
    """Schema for creating a contract."""

    template_id: Optional[int] = None
    contract_type: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    parties: List[ContractPartySchema] = Field(default_factory=list)

    # Entity linkages
    candidate_id: Optional[int] = None
    customer_id: Optional[int] = None
    supplier_id: Optional[int] = None
    requirement_id: Optional[int] = None
    offer_id: Optional[int] = None

    # Timeline
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    auto_renew: bool = False
    renewal_terms: Optional[Dict[str, Any]] = None

    # Signing
    signing_order: str = Field(default="parallel", pattern="^(parallel|sequential)$")
    signing_deadline: Optional[datetime] = None

    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContractUpdateSchema(BaseModel):
    """Schema for updating a contract."""

    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    parties: Optional[List[ContractPartySchema]] = None
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    auto_renew: Optional[bool] = None
    renewal_terms: Optional[Dict[str, Any]] = None
    signing_order: Optional[str] = Field(None, pattern="^(parallel|sequential)$")
    signing_deadline: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class ContractFromTemplateSchema(BaseModel):
    """Schema for generating contract from template."""

    template_type: str = Field(..., min_length=1, max_length=100)
    context: Dict[str, Any] = Field(...)
    parties: List[ContractPartySchema] = Field(...)
    contract_type: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=255)

    # Entity linkages
    candidate_id: Optional[int] = None
    customer_id: Optional[int] = None
    supplier_id: Optional[int] = None
    requirement_id: Optional[int] = None
    offer_id: Optional[int] = None

    # Timeline
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    signing_order: str = Field(default="parallel", pattern="^(parallel|sequential)$")


class ContractSignatureCreateSchema(BaseModel):
    """Schema for submitting a signature."""

    signature_data: str = Field(..., min_length=1)


class ContractSignatureSchema(BaseModel):
    """Schema for contract signature response."""

    id: int
    contract_id: int
    signer_name: str
    signer_email: str
    signer_role: str
    status: str
    signed_at: Optional[datetime] = None
    signature_ip: Optional[str] = None
    reminder_sent_count: int
    last_reminder_at: Optional[datetime] = None
    created_at: datetime


class ContractSignerSchema(BaseModel):
    """Schema for adding signers to a contract."""

    signer_name: str = Field(..., min_length=1, max_length=255)
    signer_email: str = Field(..., min_length=5, max_length=255)
    signer_role: str = Field(..., min_length=1, max_length=100)
    signing_order: int = Field(default=1, ge=1)


class ContractSendForSignatureSchema(BaseModel):
    """Schema for sending contract for signatures."""

    signers: List[ContractSignerSchema] = Field(...)
    signing_deadline: Optional[datetime] = None
    message: Optional[str] = None


class ContractVoidSchema(BaseModel):
    """Schema for voiding a contract."""

    reason: str = Field(..., min_length=1, max_length=500)


class ContractRenewSchema(BaseModel):
    """Schema for renewing a contract."""

    new_terms: Dict[str, Any] = Field(...)
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    auto_renew: Optional[bool] = None


class ContractSigningStatusSchema(BaseModel):
    """Schema for contract signing status."""

    contract_id: int
    status: str
    completed_signers: int
    pending_signers: int
    total_signers: int
    signing_progress: float
    signatures: List[ContractSignatureSchema]


class ContractAuditTrailEntrySchema(BaseModel):
    """Schema for audit trail entry."""

    id: int
    action: str
    actor_email: str
    actor_name: Optional[str] = None
    ip_address: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime


class ContractSchema(BaseModel):
    """Schema for contract response."""

    id: int
    template_id: Optional[int] = None
    contract_type: str
    title: str
    content: str
    status: str
    parties: List[Dict[str, Any]]

    # Entity linkages
    candidate_id: Optional[int] = None
    customer_id: Optional[int] = None
    supplier_id: Optional[int] = None
    requirement_id: Optional[int] = None
    offer_id: Optional[int] = None

    # Timeline
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    auto_renew: bool

    # Signing
    signing_order: str
    signing_deadline: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Void tracking
    voided_at: Optional[datetime] = None
    void_reason: Optional[str] = None

    # Document
    document_path: Optional[str] = None
    metadata: Dict[str, Any]

    # Timestamps
    created_at: datetime
    updated_at: datetime


class ContractDetailSchema(ContractSchema):
    """Contract schema with full signature details."""

    signatures: List[ContractSignatureSchema]
    audit_trail: List[ContractAuditTrailEntrySchema]


class ContractAnalyticsSchema(BaseModel):
    """Schema for contract analytics."""

    total_contracts: int
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    avg_signing_time_hours: float
    completion_rate: float
    expiring_soon_count: int
    total_revenue: float
    avg_contract_value: float
