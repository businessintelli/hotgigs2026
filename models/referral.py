from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, Text, Integer, Date, DateTime, Boolean, JSON, ForeignKey, Float, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel


class Referrer(BaseModel):
    """Referrer profile in the referral network."""

    __tablename__ = "referrers"
    __table_args__ = (
        Index("idx_referrer_email", "email"),
        Index("idx_referrer_referral_code", "referral_code"),
        Index("idx_referrer_is_active", "is_active"),
    )

    # Identity
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True, unique=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Referrer classification
    referrer_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Referral tracking
    referral_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    specializations: Mapped[List[str]] = mapped_column(JSON, default=list)
    network_size_estimate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    # Statistics
    total_referrals: Mapped[int] = mapped_column(Integer, default=0)
    successful_placements: Mapped[int] = mapped_column(Integer, default=0)

    # Financial tracking
    total_earnings: Mapped[float] = mapped_column(Float, default=0.0)
    pending_earnings: Mapped[float] = mapped_column(Float, default=0.0)

    # Payment details
    payment_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    payment_details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Performance tier
    tier: Mapped[str] = mapped_column(String(20), default="bronze", index=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    referrals: Mapped[List["Referral"]] = relationship(
        "Referral",
        back_populates="referrer",
        cascade="all, delete-orphan",
    )
    bonuses: Mapped[List["ReferralBonus"]] = relationship(
        "ReferralBonus",
        back_populates="referrer",
        cascade="all, delete-orphan",
    )


class Referral(BaseModel):
    """Individual referral record linking referrer to candidate."""

    __tablename__ = "referrals"
    __table_args__ = (
        Index("idx_referral_referrer_id", "referrer_id"),
        Index("idx_referral_candidate_id", "candidate_id"),
        Index("idx_referral_requirement_id", "requirement_id"),
        Index("idx_referral_status", "status"),
        Index("idx_referral_current_milestone", "current_milestone"),
    )

    referrer_id: Mapped[int] = mapped_column(ForeignKey("referrers.id"), nullable=False, index=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    requirement_id: Mapped[Optional[int]] = mapped_column(ForeignKey("requirements.id"), nullable=True, index=True)

    # Referral tracking
    referral_code_used: Mapped[str] = mapped_column(String(50), nullable=False)
    referral_link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    relationship_to_candidate: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    referral_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Status and milestones
    status: Mapped[str] = mapped_column(String(50), default="referred", nullable=False, index=True)
    is_hidden_role: Mapped[bool] = mapped_column(Boolean, default=False)
    current_milestone: Mapped[str] = mapped_column(String(50), default="referred", nullable=False, index=True)

    # Timeline
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_milestone_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    placed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    referrer: Mapped["Referrer"] = relationship(
        "Referrer",
        foreign_keys=[referrer_id],
        back_populates="referrals",
    )
    bonuses: Mapped[List["ReferralBonus"]] = relationship(
        "ReferralBonus",
        back_populates="referral",
        cascade="all, delete-orphan",
    )


class ReferralBonus(BaseModel):
    """Bonus earned from a referral at a specific milestone."""

    __tablename__ = "referral_bonuses"
    __table_args__ = (
        Index("idx_referral_bonus_referral_id", "referral_id"),
        Index("idx_referral_bonus_referrer_id", "referrer_id"),
        Index("idx_referral_bonus_status", "status"),
    )

    referral_id: Mapped[int] = mapped_column(ForeignKey("referrals.id"), nullable=False, index=True)
    referrer_id: Mapped[int] = mapped_column(ForeignKey("referrers.id"), nullable=False, index=True)
    milestone: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Bonus amount
    bonus_amount: Mapped[float] = mapped_column(Float, nullable=False)
    bonus_currency: Mapped[str] = mapped_column(String(3), default="USD")

    # Status tracking
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False, index=True)
    approved_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Payment tracking
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    payment_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    referral: Mapped["Referral"] = relationship(
        "Referral",
        foreign_keys=[referral_id],
        back_populates="bonuses",
    )
    referrer: Mapped["Referrer"] = relationship(
        "Referrer",
        foreign_keys=[referrer_id],
        back_populates="bonuses",
    )


class ReferralBonusConfig(BaseModel):
    """Configuration for referral bonus structure."""

    __tablename__ = "referral_bonus_configs"
    __table_args__ = (
        Index("idx_bonus_config_requirement_id", "requirement_id"),
        Index("idx_bonus_config_customer_id", "customer_id"),
        Index("idx_bonus_config_is_default", "is_default"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    requirement_id: Mapped[Optional[int]] = mapped_column(ForeignKey("requirements.id"), nullable=True, index=True)
    customer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("customers.id"), nullable=True, index=True)

    # Bonus structure (JSON map of milestone -> amount)
    bonus_structure: Mapped[Dict[str, float]] = mapped_column(JSON, default=dict)
    max_bonus_per_referral: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Status
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
