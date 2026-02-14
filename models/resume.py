from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, JSON, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel


class Resume(BaseModel):
    """Resume file storage model."""

    __tablename__ = "resumes"

    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    is_primary: Mapped[bool] = mapped_column(default=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    candidate = relationship("Candidate", back_populates="resumes")
    parsed_resume = relationship(
        "ParsedResume",
        back_populates="resume",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Resume(id={self.id}, candidate_id={self.candidate_id}, file_name={self.file_name})>"


class ParsedResume(BaseModel):
    """Parsed resume data model."""

    __tablename__ = "parsed_resumes"

    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), nullable=False, unique=True)
    raw_text: Mapped[Optional[str]] = mapped_column(Text)
    parsed_data: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    skills_extracted: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    experience_extracted: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    education_extracted: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    certifications_extracted: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    parsing_confidence: Mapped[Optional[float]] = mapped_column(Float)
    parser_version: Mapped[Optional[str]] = mapped_column(String(50))
    parsed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    resume = relationship("Resume", back_populates="parsed_resume")

    def __repr__(self) -> str:
        return f"<ParsedResume(id={self.id}, resume_id={self.resume_id})>"
