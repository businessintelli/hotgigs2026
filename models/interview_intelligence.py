"""Interview Intelligence models for advanced interview processing and analysis."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String,
    Text,
    Integer,
    Float,
    DateTime,
    JSON,
    ForeignKey,
    Enum,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel


class InterviewRecording(BaseModel):
    """Interview recording metadata and storage."""

    __tablename__ = "interview_recordings"

    interview_id: Mapped[int] = mapped_column(
        ForeignKey("interviews.id"), nullable=False, index=True
    )
    recording_url: Mapped[str] = mapped_column(String(500), nullable=False)
    recording_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # audio, video
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    file_size: Mapped[Optional[int]] = mapped_column(Integer)  # in bytes
    storage_path: Mapped[Optional[str]] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False
    )  # pending, processing, completed, failed
    processing_error: Mapped[Optional[str]] = mapped_column(Text)
    extra_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSON, default=dict)

    # Relationships
    interview = relationship("Interview", foreign_keys=[interview_id])
    transcript = relationship(
        "InterviewTranscript",
        back_populates="recording",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<InterviewRecording(id={self.id}, interview_id={self.interview_id}, type={self.recording_type})>"


class InterviewTranscript(BaseModel):
    """Full interview transcript with timestamped segments."""

    __tablename__ = "interview_transcripts"

    recording_id: Mapped[int] = mapped_column(
        ForeignKey("interview_recordings.id"), nullable=False, index=True
    )
    full_text: Mapped[str] = mapped_column(Text, nullable=False)
    segments: Mapped[Optional[list]] = mapped_column(
        JSON,
        default=list,
        comment="Array of {speaker, text, start_time, end_time, confidence}",
    )
    language: Mapped[str] = mapped_column(String(10), default="en")
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)

    # Relationships
    recording = relationship(
        "InterviewRecording", back_populates="transcript", foreign_keys=[recording_id]
    )

    def __repr__(self) -> str:
        return f"<InterviewTranscript(id={self.id}, recording_id={self.recording_id}, word_count={self.word_count})>"


class InterviewNote(BaseModel):
    """Structured notes from interview analysis."""

    __tablename__ = "interview_notes"

    interview_id: Mapped[int] = mapped_column(
        ForeignKey("interviews.id"), nullable=False, index=True
    )
    note_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # competency, observation, red_flag, strength
    category: Mapped[Optional[str]] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp_start: Mapped[Optional[int]] = mapped_column(Integer)  # seconds
    timestamp_end: Mapped[Optional[int]] = mapped_column(Integer)  # seconds
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(50), default="ai")  # ai or human
    supporting_quotes: Mapped[Optional[list]] = mapped_column(JSON, default=list)

    # Relationships
    interview = relationship("Interview", foreign_keys=[interview_id])

    def __repr__(self) -> str:
        return f"<InterviewNote(id={self.id}, interview_id={self.interview_id}, type={self.note_type})>"


class CompetencyScore(BaseModel):
    """Competency assessment from interview analysis."""

    __tablename__ = "competency_scores"

    interview_id: Mapped[int] = mapped_column(
        ForeignKey("interviews.id"), nullable=False, index=True
    )
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"), nullable=False, index=True
    )
    competency_name: Mapped[str] = mapped_column(String(255), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    evidence: Mapped[Optional[list]] = mapped_column(
        JSON, default=list, comment="Array of supporting quotes"
    )
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    assessed_by: Mapped[str] = mapped_column(String(50), default="ai")  # ai or human

    # Relationships
    interview = relationship("Interview", foreign_keys=[interview_id])
    candidate = relationship("Candidate", foreign_keys=[candidate_id])

    def __repr__(self) -> str:
        return f"<CompetencyScore(id={self.id}, competency={self.competency_name}, rating={self.rating})>"


class InterviewAnalytics(BaseModel):
    """Interview metrics and analytics."""

    __tablename__ = "interview_analytics"

    interview_id: Mapped[int] = mapped_column(
        ForeignKey("interviews.id"), nullable=False, unique=True, index=True
    )
    talk_time_ratio: Mapped[Optional[float]] = mapped_column(Float)  # candidate:interviewer
    question_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_response_length: Mapped[Optional[float]] = mapped_column(Float)  # words
    sentiment_overall: Mapped[Optional[str]] = mapped_column(
        String(50)
    )  # positive, neutral, negative
    sentiment_trend: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    interview_quality_score: Mapped[Optional[float]] = mapped_column(Float)  # 0-100
    bias_flags: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    question_coverage: Mapped[Optional[dict]] = mapped_column(
        JSON, default=dict, comment="Technical, behavioral, situational coverage %"
    )

    # Relationships
    interview = relationship("Interview", foreign_keys=[interview_id])

    def __repr__(self) -> str:
        return f"<InterviewAnalytics(id={self.id}, interview_id={self.interview_id})>"


class InterviewQuestion(BaseModel):
    """AI-generated interview questions."""

    __tablename__ = "interview_questions"

    interview_id: Mapped[int] = mapped_column(
        ForeignKey("interviews.id"), nullable=False, index=True
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # technical, behavioral, situational, culture_fit
    difficulty: Mapped[str] = mapped_column(String(20), default="medium")  # easy, medium, hard
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    generated_by: Mapped[str] = mapped_column(String(50), default="ai")
    context: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)  # role-specific context

    # Relationships
    interview = relationship("Interview", foreign_keys=[interview_id])
    response = relationship(
        "InterviewResponse",
        back_populates="question",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<InterviewQuestion(id={self.id}, category={self.category}, order={self.order})>"


class InterviewResponse(BaseModel):
    """Candidate response to interview questions."""

    __tablename__ = "interview_responses"

    question_id: Mapped[int] = mapped_column(
        ForeignKey("interview_questions.id"), nullable=False, unique=True
    )
    response_text: Mapped[Optional[str]] = mapped_column(Text)
    response_audio_url: Mapped[Optional[str]] = mapped_column(String(500))
    response_video_url: Mapped[Optional[str]] = mapped_column(String(500))
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    answered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    ai_score: Mapped[Optional[float]] = mapped_column(Float)  # 0-100
    evaluator_score: Mapped[Optional[float]] = mapped_column(Float)  # 0-100
    evaluation_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    question = relationship("InterviewQuestion", back_populates="response")

    def __repr__(self) -> str:
        return f"<InterviewResponse(id={self.id}, question_id={self.question_id})>"
