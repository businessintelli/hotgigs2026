"""Background import job model for tracking bulk operations."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, String, Integer, Text, JSON, Enum, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from models.base import BaseModel


class ImportJobType:
    """Import job types enum."""
    RESUME_UPLOAD = "resume_upload"
    RESUME_EXCEL = "resume_excel"
    CANDIDATE_EXCEL = "candidate_excel"
    REQUIREMENT_EXCEL = "requirement_excel"
    PLACEMENT_EXCEL = "placement_excel"
    ASSOCIATE_EXCEL = "associate_excel"
    BATCH_SCORE = "batch_score"
    SKILL_EXTRACTION = "skill_extraction"
    PLACEMENT_PREDICTION = "placement_prediction"
    MARKET_ANALYSIS = "market_analysis"

    @classmethod
    def all_types(cls):
        """Return all job types."""
        return [
            cls.RESUME_UPLOAD,
            cls.RESUME_EXCEL,
            cls.CANDIDATE_EXCEL,
            cls.REQUIREMENT_EXCEL,
            cls.PLACEMENT_EXCEL,
            cls.ASSOCIATE_EXCEL,
            cls.BATCH_SCORE,
            cls.SKILL_EXTRACTION,
            cls.PLACEMENT_PREDICTION,
            cls.MARKET_ANALYSIS,
        ]


class ImportJobStatus:
    """Import job status enum."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    COMPLETED_WITH_ERRORS = "completed_with_errors"
    FAILED = "failed"

    @classmethod
    def all_statuses(cls):
        """Return all statuses."""
        return [
            cls.QUEUED,
            cls.PROCESSING,
            cls.COMPLETED,
            cls.COMPLETED_WITH_ERRORS,
            cls.FAILED,
        ]


class ImportJob(BaseModel):
    """Tracks background import/analysis jobs with progress and failure records."""

    __tablename__ = "import_jobs"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    organization_id: Mapped[Optional[int]] = mapped_column(ForeignKey("organizations.id"), nullable=True, index=True)

    job_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="ImportJobType: RESUME_UPLOAD, RESUME_EXCEL, CANDIDATE_EXCEL, etc."
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=ImportJobStatus.QUEUED,
        index=True,
        comment="ImportJobStatus: QUEUED, PROCESSING, COMPLETED, COMPLETED_WITH_ERRORS, FAILED"
    )

    # Progress tracking
    total_records: Mapped[int] = mapped_column(Integer, default=0, comment="Total records to process")
    processed_records: Mapped[int] = mapped_column(Integer, default=0, comment="Records processed so far")
    success_count: Mapped[int] = mapped_column(Integer, default=0, comment="Successfully imported records")
    failure_count: Mapped[int] = mapped_column(Integer, default=0, comment="Failed records")
    skipped_count: Mapped[int] = mapped_column(Integer, default=0, comment="Skipped records")
    progress_percent: Mapped[float] = mapped_column(Float, default=0.0, comment="Progress 0-100")

    # Records data
    success_records: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="List of successful record summaries"
    )
    failure_records: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="List of {row_number, data, errors, field_errors}"
    )
    skipped_records: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="List of {row_number, data, reason}"
    )

    # Job configuration
    job_config: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="Original import configuration/parameters"
    )

    file_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="Original uploaded filename")

    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="If job itself failed")
    notification_sent: Mapped[bool] = mapped_column(default=False, comment="Whether completion notification was sent")
