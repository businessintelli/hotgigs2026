"""Job post models for AI-generated job posting intelligence."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Float, Date, DateTime, JSON, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel


class JobPost(BaseModel):
    """AI-generated job posting with SEO and inclusivity optimization."""

    __tablename__ = "job_posts"

    requirement_id: Mapped[int] = mapped_column(ForeignKey("requirements.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="Full HTML/markdown content")
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    responsibilities: Mapped[list] = mapped_column(JSON, default=list, nullable=False, comment="Array of strings")
    qualifications_required: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    qualifications_preferred: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    benefits: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    salary_range_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    salary_range_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    seo_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    inclusivity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        default="draft",
        nullable=False,
        comment="draft/published/archived",
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    published_boards: Mapped[list] = mapped_column(JSON, default=list, nullable=False, comment="Array of board names")
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Relationships
    requirement = relationship("Requirement")
    created_by_user = relationship("User")
    analytics = relationship(
        "JobPostAnalytics",
        back_populates="job_post",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<JobPost(id={self.id}, requirement_id={self.requirement_id}, status={self.status})>"


class JobPostAnalytics(BaseModel):
    """Analytics tracking for published job posts."""

    __tablename__ = "job_post_analytics"

    job_post_id: Mapped[int] = mapped_column(ForeignKey("job_posts.id"), nullable=False, index=True)
    board_name: Mapped[str] = mapped_column(String(100), nullable=False)
    views: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    applications: Mapped[int] = mapped_column(Integer, default=0)
    period_start: Mapped[datetime] = mapped_column(Date, nullable=False)
    period_end: Mapped[datetime] = mapped_column(Date, nullable=False)

    # Relationships
    job_post = relationship("JobPost", back_populates="analytics")

    def __repr__(self) -> str:
        return f"<JobPostAnalytics(job_post_id={self.job_post_id}, board={self.board_name}, views={self.views})>"
