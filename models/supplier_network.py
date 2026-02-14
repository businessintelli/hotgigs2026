"""Supplier network models for requirement distribution and rate card management."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Float, Date, DateTime, JSON, ForeignKey, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel


class SupplierRequirement(BaseModel):
    """Track requirement distributions to suppliers."""

    __tablename__ = "supplier_requirements"

    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), nullable=False, index=True)
    requirement_id: Mapped[int] = mapped_column(ForeignKey("requirements.id"), nullable=False, index=True)
    distributed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    response_status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
        comment="pending/accepted/declined/submitted",
    )
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    candidates_submitted: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    supplier = relationship("Supplier")
    requirement = relationship("Requirement")

    def __repr__(self) -> str:
        return f"<SupplierRequirement(supplier_id={self.supplier_id}, requirement_id={self.requirement_id}, status={self.response_status})>"


class SupplierRateCard(BaseModel):
    """Supplier rate cards for different roles and locations."""

    __tablename__ = "supplier_rate_cards"

    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), nullable=False, index=True)
    role_title: Mapped[str] = mapped_column(String(255), nullable=False)
    skill_category: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    min_rate: Mapped[float] = mapped_column(Float, nullable=False)
    max_rate: Mapped[float] = mapped_column(Float, nullable=False)
    rate_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="hourly/annual/contract",
    )
    effective_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    supplier = relationship("Supplier")

    def __repr__(self) -> str:
        return f"<SupplierRateCard(supplier_id={self.supplier_id}, role={self.role_title}, min_rate={self.min_rate})>"


class SupplierCommunication(BaseModel):
    """Track communications with suppliers."""

    __tablename__ = "supplier_communications"

    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), nullable=False, index=True)
    communication_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="requirement_distribution/follow_up/performance_review/general",
    )
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sent_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    supplier = relationship("Supplier")
    sent_by_user = relationship("User")

    def __repr__(self) -> str:
        return f"<SupplierCommunication(supplier_id={self.supplier_id}, type={self.communication_type})>"
