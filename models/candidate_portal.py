from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, Text, Integer, Date, DateTime, Boolean, JSON, ForeignKey, BigInteger, Index, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel


class CandidateProfile(BaseModel):
    """Candidate's public-facing portal profile."""

    __tablename__ = "candidate_profiles"

    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), unique=True, nullable=False, index=True)
    headline: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_enhanced_bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Links
    portfolio_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    github_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    personal_website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Preferences
    desired_roles: Mapped[List[str]] = mapped_column(JSON, default=list)
    desired_locations: Mapped[List[str]] = mapped_column(JSON, default=list)
    desired_rate_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    desired_rate_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rate_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Availability
    availability_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    availability_status: Mapped[str] = mapped_column(String(50), default="not_looking")
    work_preferences: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

    # Profile metrics
    profile_completeness: Mapped[float] = mapped_column(Float, default=0.0)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    last_active_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class CandidateVideo(BaseModel):
    """Video introduction and demonstrations from candidates."""

    __tablename__ = "candidate_videos"
    __table_args__ = (
        Index("idx_candidate_video_candidate_id", "candidate_id"),
        Index("idx_candidate_video_is_active", "is_active"),
    )

    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    video_url: Mapped[str] = mapped_column(String(500), nullable=False)
    storage_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Video metadata
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    video_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # AI-generated content
    transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    skills_mentioned: Mapped[List[str]] = mapped_column(JSON, default=list)

    # Status and metrics
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ResumeBuilderData(BaseModel):
    """Structured resume data for candidates."""

    __tablename__ = "resume_builder_data"
    __table_args__ = (
        Index("idx_resume_builder_candidate_id", "candidate_id"),
    )

    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    template_name: Mapped[str] = mapped_column(String(100), default="professional")

    # Personal information
    personal_info: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_enhanced_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Content sections
    experience: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    education: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    skills: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    certifications: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    projects: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    languages: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    custom_sections: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)

    # Generated files
    generated_pdf_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    generated_docx_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    last_generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
