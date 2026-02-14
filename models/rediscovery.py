"""Candidate rediscovery models for Metaview-style silver medalist resurfacing."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Float, JSON, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel


class CandidateRediscovery(BaseModel):
    """Track rediscovery opportunities for past candidates."""

    __tablename__ = "candidate_rediscoveries"

    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    requirement_id: Mapped[int] = mapped_column(ForeignKey("requirements.id"), nullable=False, index=True)
    original_requirement_id: Mapped[Optional[int]] = mapped_column(ForeignKey("requirements.id"), nullable=True)
    rediscovery_score: Mapped[float] = mapped_column(Float, nullable=False)
    skill_match_score: Mapped[float] = mapped_column(Float, nullable=False)
    interview_history_score: Mapped[float] = mapped_column(Float, nullable=False)
    recency_score: Mapped[float] = mapped_column(Float, nullable=False)
    engagement_score: Mapped[float] = mapped_column(Float, nullable=False)
    score_breakdown: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        default="identified",
        nullable=False,
        comment="identified/contacted/responded/resubmitted/rejected",
    )
    contacted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    candidate = relationship("Candidate")
    requirement = relationship("Requirement", foreign_keys=[requirement_id])
    original_requirement = relationship("Requirement", foreign_keys=[original_requirement_id])

    def __repr__(self) -> str:
        return f"<CandidateRediscovery(candidate_id={self.candidate_id}, requirement_id={self.requirement_id}, score={self.rediscovery_score})>"


class CompetencyProfile(BaseModel):
    """Aggregated competency profile for candidates based on interview feedback."""

    __tablename__ = "competency_profiles"

    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, unique=True, index=True)
    technical_proficiency: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    communication: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    problem_solving: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    leadership: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    culture_fit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    domain_expertise: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    adaptability: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    competency_details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    assessment_count: Mapped[int] = mapped_column(Integer, default=0)
    last_assessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    candidate = relationship("Candidate")

    def __repr__(self) -> str:
        return f"<CompetencyProfile(candidate_id={self.candidate_id}, assessments={self.assessment_count})>"
