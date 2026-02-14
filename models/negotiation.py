"""Rate negotiation and interview scheduling models."""

from datetime import datetime
from typing import Optional, Dict, List, Any
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, JSON, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel


class RateNegotiation(BaseModel):
    """Rate negotiation between recruiter, candidate, and customer."""

    __tablename__ = "rate_negotiations"

    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id"), index=True, nullable=False)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), index=True, nullable=False)
    requirement_id: Mapped[int] = mapped_column(ForeignKey("requirements.id"), index=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True, nullable=False)

    # Rate tracking
    candidate_desired_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    customer_max_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    initial_proposed_rate: Mapped[float] = mapped_column(Float, nullable=False)
    current_proposed_rate: Mapped[float] = mapped_column(Float, nullable=False)
    agreed_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rate_type: Mapped[str] = mapped_column(String(50), nullable=False)  # hourly/annual/monthly

    # Margin tracking
    bill_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pay_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    margin: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    margin_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    target_margin_percentage: Mapped[float] = mapped_column(Float, default=20.0, nullable=False)

    # Status and tracking
    status: Mapped[str] = mapped_column(String(50), default="initiated", nullable=False)  # initiated/in_progress/agreed/failed/cancelled
    total_rounds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_rounds: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    negotiated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Relationships
    rounds: "Mapped[List[NegotiationRound]]" = relationship("NegotiationRound", back_populates="negotiation", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_rate_negotiation_submission_candidate", "submission_id", "candidate_id"),
        Index("ix_rate_negotiation_status", "status"),
        Index("ix_rate_negotiation_started_at", "started_at"),
    )


class NegotiationRound(BaseModel):
    """Individual round in a rate negotiation."""

    __tablename__ = "negotiation_rounds"

    negotiation_id: Mapped[int] = mapped_column(ForeignKey("rate_negotiations.id"), index=True, nullable=False)
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    proposed_by: Mapped[str] = mapped_column(String(50), nullable=False)  # recruiter/candidate/customer/ai
    proposed_rate: Mapped[float] = mapped_column(Float, nullable=False)
    rate_type: Mapped[str] = mapped_column(String(50), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    counter_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    counter_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="proposed", nullable=False)  # proposed/countered/accepted/rejected
    proposed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationship
    negotiation: "Mapped[RateNegotiation]" = relationship("RateNegotiation", back_populates="rounds")

    __table_args__ = (
        Index("ix_negotiation_round_negotiation_number", "negotiation_id", "round_number"),
    )


class InterviewSchedule(BaseModel):
    """Interview scheduling with conflict detection and calendar integration."""

    __tablename__ = "interview_schedules"

    interview_id: Mapped[Optional[int]] = mapped_column(ForeignKey("interviews.id"), nullable=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), index=True, nullable=False)
    requirement_id: Mapped[int] = mapped_column(ForeignKey("requirements.id"), index=True, nullable=False)

    # Interview details
    interview_type: Mapped[str] = mapped_column(String(50), nullable=False)  # phone/video_zoom/video_teams/video_meet/onsite/panel
    scheduled_date: Mapped[str] = mapped_column(String(10), nullable=False)  # YYYY-MM-DD format
    scheduled_time: Mapped[str] = mapped_column(String(5), nullable=False)   # HH:MM format
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)

    # Interviewer information
    interviewer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    interviewer_email: Mapped[str] = mapped_column(String(255), nullable=False)
    additional_participants: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)  # [{name, email, role}]

    # Meeting details
    meeting_link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    meeting_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # For onsite interviews

    # Status
    status: Mapped[str] = mapped_column(String(50), default="scheduled", nullable=False)  # scheduled/confirmed/rescheduled/cancelled/completed/no_show
    confirmation_status: Mapped[Optional[Dict[str, str]]] = mapped_column(JSON, nullable=True)  # {candidate: confirmed, interviewer: pending}

    # Reschedule tracking
    reschedule_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reschedule_history: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)  # [{old_date, old_time, new_date, new_time, reason, rescheduled_by, rescheduled_at}]

    # Calendar integration
    calendar_event_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    calendar_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # google/outlook

    # Notifications
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reminder_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Notes and cancellation
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    scheduled_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

    __table_args__ = (
        Index("ix_interview_schedule_candidate_requirement", "candidate_id", "requirement_id"),
        Index("ix_interview_schedule_status", "status"),
        Index("ix_interview_schedule_scheduled_date", "scheduled_date"),
    )
