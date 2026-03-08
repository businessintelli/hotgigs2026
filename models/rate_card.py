"""Rate card models for VMS billing."""
from datetime import date
from typing import Optional
from sqlalchemy import String, Float, Date, ForeignKey, Index, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel
from models.enums import RateCardStatus


class RateCard(BaseModel):
    __tablename__ = "rate_cards"

    client_org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    job_category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    location: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    skill_level: Mapped[Optional[str]] = mapped_column(String(50))

    bill_rate_min: Mapped[float] = mapped_column(Float, nullable=False)
    bill_rate_max: Mapped[float] = mapped_column(Float, nullable=False)
    pay_rate_min: Mapped[float] = mapped_column(Float, nullable=False)
    pay_rate_max: Mapped[float] = mapped_column(Float, nullable=False)

    overtime_multiplier: Mapped[float] = mapped_column(Float, default=1.5)
    weekend_multiplier: Mapped[Optional[float]] = mapped_column(Float, default=1.25)
    shift_premium: Mapped[Optional[float]] = mapped_column(Float, default=0.0)

    currency: Mapped[str] = mapped_column(String(3), default="USD")
    effective_from: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    effective_to: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(Enum(RateCardStatus), default=RateCardStatus.ACTIVE, index=True)

    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    entries = relationship("RateCardEntry", back_populates="rate_card", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_rate_card_client_cat_loc", "client_org_id", "job_category", "location"),
        Index("ix_rate_card_effective", "effective_from", "effective_to"),
    )


class RateCardEntry(BaseModel):
    __tablename__ = "rate_card_entries"

    rate_card_id: Mapped[int] = mapped_column(ForeignKey("rate_cards.id"), nullable=False, index=True)
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    skill_level: Mapped[str] = mapped_column(String(50), nullable=False)
    bill_rate: Mapped[Optional[float]] = mapped_column(Float)
    pay_rate: Mapped[Optional[float]] = mapped_column(Float)

    rate_card = relationship("RateCard", back_populates="entries")
