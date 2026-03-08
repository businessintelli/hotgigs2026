"""Compliance tracking models."""
from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Boolean, Date, DateTime, ForeignKey, Index, Text, Float, Enum
from sqlalchemy.orm import Mapped, mapped_column
from models.base import BaseModel
from models.enums import ComplianceStatus, ComplianceType


class ComplianceRequirement(BaseModel):
    __tablename__ = "compliance_requirements"

    organization_id: Mapped[Optional[int]] = mapped_column(ForeignKey("organizations.id"), index=True)
    requirement_type: Mapped[str] = mapped_column(Enum(ComplianceType), nullable=False, index=True)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    certification_name: Mapped[Optional[str]] = mapped_column(String(200))
    issuing_body: Mapped[Optional[str]] = mapped_column(String(200))
    renewal_frequency_days: Mapped[Optional[int]] = mapped_column(nullable=True)
    risk_level: Mapped[str] = mapped_column(String(50), default="medium")
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    __table_args__ = (
        Index("ix_compliance_req_org_type", "organization_id", "requirement_type"),
    )


class ComplianceRecord(BaseModel):
    __tablename__ = "compliance_records"

    placement_id: Mapped[int] = mapped_column(ForeignKey("placement_records.id"), nullable=False, index=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    compliance_requirement_id: Mapped[int] = mapped_column(ForeignKey("compliance_requirements.id"), nullable=False)
    status: Mapped[str] = mapped_column(Enum(ComplianceStatus), default=ComplianceStatus.NOT_STARTED, index=True)
    required_by: Mapped[Optional[date]] = mapped_column(Date)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    verified_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    verification_date: Mapped[Optional[date]] = mapped_column(Date)
    verification_notes: Mapped[Optional[str]] = mapped_column(Text)
    provider_name: Mapped[Optional[str]] = mapped_column(String(200))
    provider_reference_id: Mapped[Optional[str]] = mapped_column(String(255))
    passed: Mapped[Optional[bool]] = mapped_column(Boolean)
    risk_score: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (
        Index("ix_compliance_placement_status", "placement_id", "status"),
        Index("ix_compliance_candidate_expires", "candidate_id", "expires_at"),
    )


class ComplianceScore(BaseModel):
    __tablename__ = "compliance_scores"

    supplier_org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False, unique=True)
    overall_score: Mapped[float] = mapped_column(Float, default=100.0)
    completed_requirements: Mapped[int] = mapped_column(nullable=False, default=0)
    total_requirements: Mapped[int] = mapped_column(nullable=False, default=0)
    expired_requirements: Mapped[int] = mapped_column(nullable=False, default=0)
    failed_requirements: Mapped[int] = mapped_column(nullable=False, default=0)
    last_calculated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
