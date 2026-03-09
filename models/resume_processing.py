"""
Resume Processing Models — thumbnails, PDF conversion, download tracking, condensation.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, JSON, ForeignKey, DateTime, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel


class ResumeThumbnail(BaseModel):
    """Resume thumbnail/preview image model."""

    __tablename__ = "resume_thumbnails"

    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), nullable=False, unique=True, index=True)
    thumbnail_path: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_format: Mapped[str] = mapped_column(String(20), default="png")
    width: Mapped[int] = mapped_column(Integer, default=200)
    height: Mapped[int] = mapped_column(Integer, default=280)
    page_count: Mapped[int] = mapped_column(Integer, default=1)
    preview_text: Mapped[Optional[str]] = mapped_column(Text)  # First ~500 chars for text preview
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<ResumeThumbnail(id={self.id}, resume_id={self.resume_id})>"


class ResumeConversion(BaseModel):
    """Track DOCX-to-PDF conversion for uniform storage."""

    __tablename__ = "resume_conversions"

    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), nullable=False, index=True)
    original_format: Mapped[str] = mapped_column(String(20), nullable=False)  # docx, doc, rtf
    converted_format: Mapped[str] = mapped_column(String(20), default="pdf")
    original_path: Mapped[str] = mapped_column(String(500), nullable=False)
    converted_path: Mapped[str] = mapped_column(String(500), nullable=False)
    original_size: Mapped[int] = mapped_column(Integer, nullable=False)
    converted_size: Mapped[int] = mapped_column(Integer, nullable=False)
    conversion_status: Mapped[str] = mapped_column(String(20), default="completed")  # pending, converting, completed, failed
    conversion_error: Mapped[Optional[str]] = mapped_column(Text)
    converted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<ResumeConversion(id={self.id}, resume_id={self.resume_id}, {self.original_format}→{self.converted_format})>"


class ResumeDownloadLog(BaseModel):
    """Track when recruiters view or download candidate resumes."""

    __tablename__ = "resume_download_logs"

    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), nullable=False, index=True)
    candidate_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    recruiter_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    recruiter_name: Mapped[Optional[str]] = mapped_column(String(255))
    recruiter_email: Mapped[Optional[str]] = mapped_column(String(255))
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # view, download, preview, print
    source_page: Mapped[Optional[str]] = mapped_column(String(100))  # ats_workflow, candidate_crm, search, etc.
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    organization_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    accessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<ResumeDownloadLog(id={self.id}, resume_id={self.resume_id}, action={self.action})>"


class CondensedResume(BaseModel):
    """AI-condensed 3-page resume summary with key stats and strong points."""

    __tablename__ = "condensed_resumes"

    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), nullable=False, index=True)
    candidate_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Condensed content
    condensed_html: Mapped[Optional[str]] = mapped_column(Text)  # Formatted HTML for rendering
    condensed_text: Mapped[Optional[str]] = mapped_column(Text)  # Plain text version
    condensed_pdf_path: Mapped[Optional[str]] = mapped_column(String(500))  # Generated PDF path

    # Extracted highlights
    professional_summary: Mapped[Optional[str]] = mapped_column(Text)  # 3-5 sentence summary
    key_stats: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    # e.g. {"years_experience": 12, "certifications": 3, "industries": ["tech","finance"], "projects_led": 8}
    strong_points: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    # e.g. ["10+ years Python", "Led team of 20", "AWS Solutions Architect Certified"]
    career_trajectory: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    # Condensed timeline of roles
    top_skills: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    # Ranked top skills with proficiency
    notable_achievements: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    # Top achievements from entire career

    # Metadata
    original_page_count: Mapped[int] = mapped_column(Integer, default=0)
    condensed_page_count: Mapped[int] = mapped_column(Integer, default=3)
    compression_ratio: Mapped[Optional[float]] = mapped_column(Float)  # e.g. 0.33 if 9 pages → 3
    ai_model_used: Mapped[Optional[str]] = mapped_column(String(100))
    condensation_quality: Mapped[Optional[float]] = mapped_column(Float)  # 0-1 confidence score
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<CondensedResume(id={self.id}, resume_id={self.resume_id}, {self.original_page_count}→{self.condensed_page_count} pages)>"
