from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Float, JSON, ForeignKey, DateTime, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel
from models.enums import MatchStatus


class MatchScore(BaseModel):
    """Candidate-to-requirement match scoring model."""

    __tablename__ = "match_scores"

    requirement_id: Mapped[int] = mapped_column(ForeignKey("requirements.id"), nullable=False, index=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    skill_score: Mapped[Optional[float]] = mapped_column(Float)
    experience_score: Mapped[Optional[float]] = mapped_column(Float)
    education_score: Mapped[Optional[float]] = mapped_column(Float)
    location_score: Mapped[Optional[float]] = mapped_column(Float)
    rate_score: Mapped[Optional[float]] = mapped_column(Float)
    availability_score: Mapped[Optional[float]] = mapped_column(Float)
    culture_score: Mapped[Optional[float]] = mapped_column(Float)
    score_breakdown: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    missing_skills: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    standout_qualities: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(
        Enum(MatchStatus),
        default=MatchStatus.PENDING,
        nullable=False,
        index=True,
    )
    matched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    matched_by: Mapped[Optional[str]] = mapped_column(String(50), default="system")
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    requirement = relationship("Requirement", back_populates="match_scores")
    candidate = relationship("Candidate", back_populates="match_scores")
    submissions = relationship("Submission", back_populates="match_score")

    def __repr__(self) -> str:
        return f"<MatchScore(id={self.id}, requirement_id={self.requirement_id}, candidate_id={self.candidate_id}, score={self.overall_score})>"
