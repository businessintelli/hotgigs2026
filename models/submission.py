from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Float, DateTime, JSON, ForeignKey, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel
from models.enums import SubmissionStatus


class Submission(BaseModel):
    """Candidate submission to customer model."""

    __tablename__ = "submissions"

    requirement_id: Mapped[int] = mapped_column(ForeignKey("requirements.id"), nullable=False, index=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False, index=True)
    supplier_id: Mapped[Optional[int]] = mapped_column(ForeignKey("suppliers.id"), nullable=True)
    match_score_id: Mapped[Optional[int]] = mapped_column(ForeignKey("match_scores.id"))
    submitted_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(SubmissionStatus),
        default=SubmissionStatus.DRAFT,
        nullable=False,
        index=True,
    )
    internal_notes: Mapped[Optional[str]] = mapped_column(Text)
    customer_notes: Mapped[Optional[str]] = mapped_column(Text)
    resume_version_used: Mapped[Optional[int]] = mapped_column(default=1)
    rate_proposed: Mapped[Optional[float]] = mapped_column(Float)
    match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    reviewed_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    submitted_to_customer_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    customer_response: Mapped[Optional[str]] = mapped_column(String(500))
    customer_response_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)
    extra_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSON, default=dict)

    # Relationships
    requirement = relationship("Requirement", back_populates="submissions")
    candidate = relationship("Candidate", back_populates="submissions")
    customer = relationship("Customer", back_populates="submissions")
    match_score = relationship("MatchScore", back_populates="submissions")
    submitted_by_user = relationship("User", foreign_keys=[submitted_by])
    reviewed_by_user = relationship("User", foreign_keys=[reviewed_by])

    def __repr__(self) -> str:
        return f"<Submission(id={self.id}, candidate_id={self.candidate_id}, requirement_id={self.requirement_id}, status={self.status})>"
