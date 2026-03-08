from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Boolean, DateTime, JSON, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel
from models.enums import ActivityType, NoteType, CommunicationDirection, CommunicationChannel


class CandidateActivity(BaseModel):
    """Activity timeline for a candidate."""

    __tablename__ = "candidate_activities"

    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    activity_type: Mapped[str] = mapped_column(
        Enum(ActivityType),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    performed_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    activity_metadata: Mapped[Optional[dict]] = mapped_column("activity_metadata", JSON, default=dict)

    # Relationships
    candidate = relationship("Candidate", foreign_keys=[candidate_id])
    performed_by_user = relationship("User", foreign_keys=[performed_by])

    def __repr__(self) -> str:
        return f"<CandidateActivity(id={self.id}, candidate_id={self.candidate_id}, type={self.activity_type})>"


class CandidateNote(BaseModel):
    """Notes on a candidate."""

    __tablename__ = "candidate_notes"

    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    note_type: Mapped[str] = mapped_column(
        Enum(NoteType),
        default=NoteType.GENERAL,
        nullable=False,
    )
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    candidate = relationship("Candidate", foreign_keys=[candidate_id])
    author = relationship("User", foreign_keys=[author_id])

    def __repr__(self) -> str:
        return f"<CandidateNote(id={self.id}, candidate_id={self.candidate_id})>"


class CandidateTag(BaseModel):
    """Tags for candidate segmentation."""

    __tablename__ = "candidate_tags"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    color: Mapped[str] = mapped_column(String(20), default="3B82F6")
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    associations = relationship("CandidateTagAssociation", back_populates="tag", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<CandidateTag(id={self.id}, name={self.name})>"


class CandidateTagAssociation(BaseModel):
    """Many-to-many association between candidates and tags."""

    __tablename__ = "candidate_tag_associations"
    __table_args__ = (UniqueConstraint("candidate_id", "tag_id", name="uq_candidate_tag"),)

    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("candidate_tags.id"), nullable=False, index=True)
    tagged_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationships
    candidate = relationship("Candidate", foreign_keys=[candidate_id])
    tag = relationship("CandidateTag", back_populates="associations", foreign_keys=[tag_id])
    tagged_by_user = relationship("User", foreign_keys=[tagged_by])

    def __repr__(self) -> str:
        return f"<CandidateTagAssociation(candidate_id={self.candidate_id}, tag_id={self.tag_id})>"


class CommunicationLog(BaseModel):
    """Email/call/message history with candidates."""

    __tablename__ = "communication_logs"

    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(
        Enum(CommunicationDirection),
        nullable=False,
        index=True,
    )
    channel: Mapped[str] = mapped_column(
        Enum(CommunicationChannel),
        nullable=False,
        index=True,
    )
    subject: Mapped[Optional[str]] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sent_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    candidate = relationship("Candidate", foreign_keys=[candidate_id])
    sent_by_user = relationship("User", foreign_keys=[sent_by])

    def __repr__(self) -> str:
        return f"<CommunicationLog(id={self.id}, candidate_id={self.candidate_id}, channel={self.channel})>"
