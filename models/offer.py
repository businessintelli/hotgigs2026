from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Float, Date, DateTime, JSON, ForeignKey, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel
from models.enums import OfferStatus, OnboardingStatus


class Offer(BaseModel):
    """Job offer model."""

    __tablename__ = "offers"

    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id"), nullable=False)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    requirement_id: Mapped[int] = mapped_column(ForeignKey("requirements.id"), nullable=False, index=True)
    offered_rate: Mapped[Optional[float]] = mapped_column(Float)
    rate_type: Mapped[Optional[str]] = mapped_column(String(50))
    start_date: Mapped[Optional[datetime]] = mapped_column(Date)
    end_date: Mapped[Optional[datetime]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(
        Enum(OfferStatus),
        default=OfferStatus.DRAFT,
        nullable=False,
        index=True,
    )
    offer_letter_path: Mapped[Optional[str]] = mapped_column(String(500))
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    response_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    negotiation_history: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    submission = relationship("Submission")
    candidate = relationship("Candidate", back_populates="offers")
    requirement = relationship("Requirement", back_populates="offers")
    onboarding = relationship(
        "Onboarding",
        back_populates="offer",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Offer(id={self.id}, candidate_id={self.candidate_id}, status={self.status})>"


class Onboarding(BaseModel):
    """Candidate onboarding tracking model."""

    __tablename__ = "onboardings"

    offer_id: Mapped[int] = mapped_column(ForeignKey("offers.id"), nullable=False, unique=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        Enum(OnboardingStatus),
        default=OnboardingStatus.NOT_STARTED,
        nullable=False,
        index=True,
    )
    checklist: Mapped[Optional[list]] = mapped_column(
        JSON,
        default=list,
        comment="Array of {item, completed, completed_at}",
    )
    documents_collected: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    background_check_status: Mapped[Optional[str]] = mapped_column(String(100))
    start_date_confirmed: Mapped[Optional[datetime]] = mapped_column(Date)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    offer = relationship("Offer", back_populates="onboarding")

    def __repr__(self) -> str:
        return f"<Onboarding(id={self.id}, candidate_id={self.candidate_id}, status={self.status})>"
