from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Float, Date, DateTime, JSON, ForeignKey, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel
from models.enums import SupplierTier


class Supplier(BaseModel):
    """Third-party supplier/staffing agency model."""

    __tablename__ = "suppliers"

    company_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    contact_name: Mapped[Optional[str]] = mapped_column(String(255))
    contact_email: Mapped[Optional[str]] = mapped_column(String(255))
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20))
    website: Mapped[Optional[str]] = mapped_column(String(255))
    specializations: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    locations_served: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    tier: Mapped[str] = mapped_column(
        Enum(SupplierTier),
        default=SupplierTier.NEW,
        nullable=False,
    )
    commission_rate: Mapped[Optional[float]] = mapped_column(Float)
    contract_start: Mapped[Optional[datetime]] = mapped_column(Date)
    contract_end: Mapped[Optional[datetime]] = mapped_column(Date)
    total_submissions: Mapped[int] = mapped_column(default=0)
    total_placements: Mapped[int] = mapped_column(default=0)
    avg_time_to_submit: Mapped[Optional[float]] = mapped_column(Float)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    performance_records = relationship(
        "SupplierPerformance",
        back_populates="supplier",
        cascade="all, delete-orphan",
    )
    candidates = relationship("Candidate")

    def __repr__(self) -> str:
        return f"<Supplier(id={self.id}, company_name={self.company_name}, tier={self.tier})>"


class SupplierPerformance(BaseModel):
    """Supplier performance metrics by period."""

    __tablename__ = "supplier_performance"

    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), nullable=False, index=True)
    period_start: Mapped[datetime] = mapped_column(Date, nullable=False)
    period_end: Mapped[datetime] = mapped_column(Date, nullable=False)
    submissions_count: Mapped[int] = mapped_column(default=0)
    placements_count: Mapped[int] = mapped_column(default=0)
    rejection_rate: Mapped[Optional[float]] = mapped_column(Float)
    avg_match_score: Mapped[Optional[float]] = mapped_column(Float)
    avg_time_to_fill: Mapped[Optional[float]] = mapped_column(Float)
    quality_score: Mapped[Optional[float]] = mapped_column(Float)
    responsiveness_score: Mapped[Optional[float]] = mapped_column(Float)
    overall_rating: Mapped[Optional[float]] = mapped_column(Float)

    # Relationships
    supplier = relationship("Supplier", back_populates="performance_records")

    def __repr__(self) -> str:
        return f"<SupplierPerformance(id={self.id}, supplier_id={self.supplier_id}, period={self.period_start} to {self.period_end})>"
