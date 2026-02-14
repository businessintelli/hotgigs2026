from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, Text, Integer, Date, DateTime, Boolean, JSON, ForeignKey, BigInteger, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel
from models.enums import ContractStatus, ContractType, ContractSignatureStatus, ContractAuditAction


class ContractTemplate(BaseModel):
    """Contract template for generating contracts from predefined structures."""

    __tablename__ = "contract_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    template_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationships
    contracts: Mapped[List["Contract"]] = relationship(
        "Contract",
        foreign_keys="Contract.template_id",
        back_populates="template",
    )


class Contract(BaseModel):
    """Main contract entity with full lifecycle management."""

    __tablename__ = "contracts"
    __table_args__ = (
        Index("idx_contract_status", "status"),
        Index("idx_contract_candidate_id", "candidate_id"),
        Index("idx_contract_customer_id", "customer_id"),
        Index("idx_contract_supplier_id", "supplier_id"),
        Index("idx_contract_requirement_id", "requirement_id"),
        Index("idx_contract_expiry_date", "expiry_date"),
    )

    template_id: Mapped[Optional[int]] = mapped_column(ForeignKey("contract_templates.id"), nullable=True)
    contract_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=ContractStatus.DRAFT.value, nullable=False, index=True)
    parties: Mapped[Dict[str, Any]] = mapped_column(JSON, default=list)

    # Entity linkages (nullable - contract can relate to any entity)
    candidate_id: Mapped[Optional[int]] = mapped_column(ForeignKey("candidates.id"), nullable=True)
    customer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("customers.id"), nullable=True)
    supplier_id: Mapped[Optional[int]] = mapped_column(ForeignKey("suppliers.id"), nullable=True)
    requirement_id: Mapped[Optional[int]] = mapped_column(ForeignKey("requirements.id"), nullable=True)
    offer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("offers.id"), nullable=True)

    # Timeline fields
    effective_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=False)
    renewal_terms: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Signature tracking
    signing_order: Mapped[str] = mapped_column(String(20), default="parallel")
    signing_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Void/cancellation tracking
    voided_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    void_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Document storage
    document_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    extra_metadata: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationships
    template: Mapped[Optional["ContractTemplate"]] = relationship(
        "ContractTemplate",
        foreign_keys=[template_id],
        back_populates="contracts",
    )
    signatures: Mapped[List["ContractSignature"]] = relationship(
        "ContractSignature",
        back_populates="contract",
        cascade="all, delete-orphan",
    )
    audit_trail: Mapped[List["ContractAuditTrail"]] = relationship(
        "ContractAuditTrail",
        back_populates="contract",
        cascade="all, delete-orphan",
    )


class ContractSignature(BaseModel):
    """Track signatures for each party on a contract."""

    __tablename__ = "contract_signatures"
    __table_args__ = (
        Index("idx_contract_signature_contract_id", "contract_id"),
        Index("idx_contract_signature_token", "signing_token"),
        Index("idx_contract_signature_email", "signer_email"),
        Index("idx_contract_signature_status", "status"),
    )

    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id"), nullable=False)
    signer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    signer_email: Mapped[str] = mapped_column(String(255), nullable=False)
    signer_role: Mapped[str] = mapped_column(String(100), nullable=False)

    # Token-based signing link
    signing_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    token_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Signature status tracking
    status: Mapped[str] = mapped_column(String(50), default=ContractSignatureStatus.PENDING.value, nullable=False, index=True)
    signed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Signature data (base64 image or hash)
    signature_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    signature_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    signature_user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Decline tracking
    decline_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Signing order for sequential workflows
    signing_order: Mapped[int] = mapped_column(Integer, default=1)

    # Reminder tracking
    reminder_sent_count: Mapped[int] = mapped_column(Integer, default=0)
    last_reminder_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    contract: Mapped["Contract"] = relationship(
        "Contract",
        foreign_keys=[contract_id],
        back_populates="signatures",
    )


class ContractAuditTrail(BaseModel):
    """Audit trail for contract lifecycle events."""

    __tablename__ = "contract_audit_trail"
    __table_args__ = (
        Index("idx_contract_audit_contract_id", "contract_id"),
        Index("idx_contract_audit_action", "action"),
        Index("idx_contract_audit_timestamp", "timestamp"),
    )

    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    actor_email: Mapped[str] = mapped_column(String(255), nullable=False)
    actor_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    contract: Mapped["Contract"] = relationship(
        "Contract",
        foreign_keys=[contract_id],
        back_populates="audit_trail",
    )
