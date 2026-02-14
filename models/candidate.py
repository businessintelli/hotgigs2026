from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Float, Date, JSON, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel
from models.enums import CandidateStatus


class Candidate(BaseModel):
    """Candidate model."""

    __tablename__ = "candidates"

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500))
    location_city: Mapped[Optional[str]] = mapped_column(String(100))
    location_state: Mapped[Optional[str]] = mapped_column(String(100))
    location_country: Mapped[Optional[str]] = mapped_column(String(100))
    current_title: Mapped[Optional[str]] = mapped_column(String(255))
    current_company: Mapped[Optional[str]] = mapped_column(String(255))
    total_experience_years: Mapped[Optional[float]] = mapped_column(Float)
    skills: Mapped[Optional[list]] = mapped_column(
        JSON,
        default=list,
        comment="Array of {skill, level, years}",
    )
    education: Mapped[Optional[list]] = mapped_column(
        JSON,
        default=list,
        comment="Array of {degree, field, institution, year}",
    )
    certifications: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    desired_rate: Mapped[Optional[float]] = mapped_column(Float)
    desired_rate_type: Mapped[Optional[str]] = mapped_column(String(50))
    availability_date: Mapped[Optional[datetime]] = mapped_column(Date)
    work_authorization: Mapped[Optional[str]] = mapped_column(String(100))
    willing_to_relocate: Mapped[Optional[bool]] = mapped_column(default=False)
    status: Mapped[str] = mapped_column(
        Enum(CandidateStatus),
        default=CandidateStatus.SOURCED,
        nullable=False,
        index=True,
    )
    source: Mapped[Optional[str]] = mapped_column(String(100))
    source_detail: Mapped[Optional[str]] = mapped_column(String(500))
    supplier_id: Mapped[Optional[int]] = mapped_column(ForeignKey("suppliers.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    engagement_score: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    last_contacted_at: Mapped[Optional[datetime]] = mapped_column(Date)
    extra_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSON, default=dict)

    # Relationships
    resumes = relationship("Resume", back_populates="candidate", cascade="all, delete-orphan")
    match_scores = relationship("MatchScore", back_populates="candidate", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="candidate", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="candidate", cascade="all, delete-orphan")
    offers = relationship("Offer", back_populates="candidate", cascade="all, delete-orphan")
    supplier = relationship("Supplier")

    def __repr__(self) -> str:
        return f"<Candidate(id={self.id}, name={self.first_name} {self.last_name}, status={self.status})>"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
