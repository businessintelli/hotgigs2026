from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, DateTime, JSON, ForeignKey, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel
from models.enums import InterviewType, InterviewStatus


class Interview(BaseModel):
    """Interview scheduling and tracking model."""

    __tablename__ = "interviews"

    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    requirement_id: Mapped[int] = mapped_column(ForeignKey("requirements.id"), nullable=False, index=True)
    interview_type: Mapped[str] = mapped_column(Enum(InterviewType), nullable=False)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(
        Enum(InterviewStatus),
        default=InterviewStatus.SCHEDULED,
        nullable=False,
        index=True,
    )
    interviewer_name: Mapped[Optional[str]] = mapped_column(String(255))
    interviewer_email: Mapped[Optional[str]] = mapped_column(String(255))
    meeting_link: Mapped[Optional[str]] = mapped_column(String(500))
    recording_url: Mapped[Optional[str]] = mapped_column(String(500))
    transcript_url: Mapped[Optional[str]] = mapped_column(String(500))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    ai_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="AI interview score 0-5")
    extra_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSON, default=dict)

    # Relationships
    candidate = relationship("Candidate", back_populates="interviews")
    requirement = relationship("Requirement", back_populates="interviews")
    feedback = relationship(
        "InterviewFeedback",
        back_populates="interview",
        uselist=False,
        cascade="all, delete-orphan",
    )
    recordings = relationship(
        "InterviewRecording",
        foreign_keys="InterviewRecording.interview_id",
        cascade="all, delete-orphan",
    )
    questions = relationship(
        "InterviewQuestion",
        foreign_keys="InterviewQuestion.interview_id",
        cascade="all, delete-orphan",
    )
    notes = relationship(
        "InterviewNote",
        foreign_keys="InterviewNote.interview_id",
        cascade="all, delete-orphan",
    )
    competency_scores = relationship(
        "CompetencyScore",
        foreign_keys="CompetencyScore.interview_id",
        cascade="all, delete-orphan",
    )
    analytics = relationship(
        "InterviewAnalytics",
        back_populates="interview",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Interview(id={self.id}, candidate_id={self.candidate_id}, type={self.interview_type})>"


class InterviewFeedback(BaseModel):
    """Interview feedback and evaluation model."""

    __tablename__ = "interview_feedbacks"

    interview_id: Mapped[int] = mapped_column(ForeignKey("interviews.id"), nullable=False, unique=True)
    evaluator: Mapped[Optional[str]] = mapped_column(String(255))
    overall_rating: Mapped[Optional[int]] = mapped_column(Integer)
    technical_rating: Mapped[Optional[int]] = mapped_column(Integer)
    communication_rating: Mapped[Optional[int]] = mapped_column(Integer)
    culture_fit_rating: Mapped[Optional[int]] = mapped_column(Integer)
    problem_solving_rating: Mapped[Optional[int]] = mapped_column(Integer)
    strengths: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    weaknesses: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    recommendation: Mapped[Optional[str]] = mapped_column(String(50))
    detailed_notes: Mapped[Optional[str]] = mapped_column(Text)
    scorecard_data: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    ai_generated: Mapped[bool] = mapped_column(default=False)

    # Relationships
    interview = relationship("Interview", back_populates="feedback")

    def __repr__(self) -> str:
        return f"<InterviewFeedback(id={self.id}, interview_id={self.interview_id})>"
