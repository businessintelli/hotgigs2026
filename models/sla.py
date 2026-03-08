"""SLA configuration and breach tracking models."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Index, Text, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel
from models.enums import SLAMetric, SLASeverity


class SLAConfiguration(BaseModel):
    __tablename__ = "sla_configurations"

    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    response_time_hours: Mapped[Optional[int]] = mapped_column(Integer)
    fill_time_days: Mapped[Optional[int]] = mapped_column(Integer)
    min_quality_score: Mapped[Optional[float]] = mapped_column(Float)
    min_acceptance_rate: Mapped[Optional[float]] = mapped_column(Float)
    min_retention_days: Mapped[Optional[int]] = mapped_column(Integer)

    response_time_penalty: Mapped[float] = mapped_column(Float, default=100.0)
    fill_time_penalty: Mapped[float] = mapped_column(Float, default=0.0)
    quality_penalty_per_point: Mapped[float] = mapped_column(Float, default=0.0)
    penalty_calculation: Mapped[str] = mapped_column(String(50), default="cumulative")

    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    breaches = relationship("SLABreachRecord", back_populates="sla_config", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_sla_config_org_active", "organization_id", "is_active"),
    )


class SLABreachRecord(BaseModel):
    __tablename__ = "sla_breach_records"

    sla_config_id: Mapped[int] = mapped_column(ForeignKey("sla_configurations.id"), nullable=False, index=True)
    requirement_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    supplier_org_id: Mapped[Optional[int]] = mapped_column(ForeignKey("organizations.id"))

    metric_type: Mapped[str] = mapped_column(Enum(SLAMetric), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(Enum(SLASeverity), default=SLASeverity.MEDIUM, index=True)

    threshold_value: Mapped[float] = mapped_column(Float, nullable=False)
    actual_value: Mapped[float] = mapped_column(Float, nullable=False)
    variance: Mapped[float] = mapped_column(Float, nullable=False)
    penalty_amount: Mapped[Optional[float]] = mapped_column(Float)

    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    resolved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text)

    sla_config = relationship("SLAConfiguration", back_populates="breaches")

    __table_args__ = (
        Index("ix_sla_breach_config_metric", "sla_config_id", "metric_type"),
        Index("ix_sla_breach_severity", "severity", "resolved_at"),
    )
