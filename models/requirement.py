from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, Date, JSON, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel
from models.enums import RequirementStatus, Priority


class Requirement(BaseModel):
    """Job requirement model."""

    __tablename__ = "requirements"

    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    skills_required: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    skills_preferred: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    experience_min: Mapped[Optional[float]] = mapped_column(Float)
    experience_max: Mapped[Optional[float]] = mapped_column(Float)
    education_level: Mapped[Optional[str]] = mapped_column(String(100))
    certifications: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    employment_type: Mapped[Optional[str]] = mapped_column(String(50))
    work_mode: Mapped[Optional[str]] = mapped_column(String(50))
    location_city: Mapped[Optional[str]] = mapped_column(String(100))
    location_state: Mapped[Optional[str]] = mapped_column(String(100))
    location_country: Mapped[Optional[str]] = mapped_column(String(100))
    rate_min: Mapped[Optional[float]] = mapped_column(Float)
    rate_max: Mapped[Optional[float]] = mapped_column(Float)
    rate_type: Mapped[Optional[str]] = mapped_column(String(50))
    duration_months: Mapped[Optional[int]] = mapped_column(Integer)
    positions_count: Mapped[int] = mapped_column(Integer, default=1)
    positions_filled: Mapped[int] = mapped_column(Integer, default=0)
    priority: Mapped[Optional[str]] = mapped_column(Enum(Priority), default=Priority.MEDIUM)
    status: Mapped[str] = mapped_column(
        Enum(RequirementStatus),
        default=RequirementStatus.DRAFT,
        nullable=False,
        index=True,
    )
    assigned_recruiter_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    submission_deadline: Mapped[Optional[datetime]] = mapped_column(Date)
    start_date: Mapped[Optional[datetime]] = mapped_column(Date)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    extra_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSON, default=dict)

    # Relationships
    customer = relationship("Customer", back_populates="requirements")
    assigned_recruiter = relationship("User")
    match_scores = relationship("MatchScore", back_populates="requirement", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="requirement", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="requirement", cascade="all, delete-orphan")
    offers = relationship("Offer", back_populates="requirement", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Requirement(id={self.id}, title={self.title}, status={self.status})>"
