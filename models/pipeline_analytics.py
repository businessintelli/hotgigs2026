"""Pipeline analytics models — conversion tracking, cohort analysis, bottleneck detection."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, DateTime, JSON, ForeignKey, Text, Index, func
from sqlalchemy.orm import Mapped, mapped_column
from models.base import BaseModel


class PipelineConversion(BaseModel):
    """Tracks actual conversion events between pipeline phases."""

    __tablename__ = "pipeline_conversions"

    job_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    organization_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    candidate_id: Mapped[int] = mapped_column(Integer, nullable=False)
    from_phase: Mapped[str] = mapped_column(String(50), nullable=False)
    to_phase: Mapped[str] = mapped_column(String(50), nullable=False)
    transitioned_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    time_in_phase_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    transitioned_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_conversion_job_phases", "job_id", "from_phase", "to_phase"),
    )


class PipelineSnapshot(BaseModel):
    """Daily snapshot of pipeline state per job for trend analysis."""

    __tablename__ = "pipeline_snapshots"

    job_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    snapshot_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    phase_counts: Mapped[dict] = mapped_column(JSON, default=dict)
    total_candidates: Mapped[int] = mapped_column(Integer, default=0)
    conversion_rates: Mapped[dict] = mapped_column(JSON, default=dict)
    avg_time_per_phase: Mapped[dict] = mapped_column(JSON, default=dict)
    bottleneck_phase: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)


class EmailNotificationLog(BaseModel):
    """Tracks all candidate email notifications sent."""

    __tablename__ = "email_notification_logs"

    candidate_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    candidate_email: Mapped[str] = mapped_column(String(255), nullable=False)
    candidate_name: Mapped[str] = mapped_column(String(255), nullable=False)
    job_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    job_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False)
    old_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    new_status: Mapped[str] = mapped_column(String(50), nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    template_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="sent")
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)

    __table_args__ = (
        Index("ix_email_log_candidate_type", "candidate_id", "notification_type"),
    )


class EmailTemplate(BaseModel):
    """Reusable email templates for status change notifications."""

    __tablename__ = "email_templates"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    trigger_event: Mapped[str] = mapped_column(String(50), nullable=False)
    subject_template: Mapped[str] = mapped_column(String(500), nullable=False)
    body_html: Mapped[str] = mapped_column(Text, nullable=False)
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    variables: Mapped[dict] = mapped_column(JSON, default=dict)
    organization_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


class InterviewScoringRubric(BaseModel):
    """Custom scoring rubrics for different job roles/interview stages."""

    __tablename__ = "interview_scoring_rubrics"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    job_role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    interview_stage: Mapped[str] = mapped_column(String(50), default="general")
    organization_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    criteria: Mapped[list] = mapped_column(JSON, default=list)
    weight_config: Mapped[dict] = mapped_column(JSON, default=dict)
    scale_min: Mapped[int] = mapped_column(Integer, default=1)
    scale_max: Mapped[int] = mapped_column(Integer, default=5)
    is_active: Mapped[bool] = mapped_column(default=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


class InterviewFeedbackSubmission(BaseModel):
    """Structured feedback submissions using rubric-based scoring."""

    __tablename__ = "interview_feedback_submissions"

    interview_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    rubric_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    interviewer_id: Mapped[int] = mapped_column(Integer, nullable=False)
    interviewer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    candidate_id: Mapped[int] = mapped_column(Integer, nullable=False)
    job_id: Mapped[int] = mapped_column(Integer, nullable=False)
    interview_stage: Mapped[str] = mapped_column(String(50), nullable=False)
    criteria_scores: Mapped[dict] = mapped_column(JSON, default=dict)
    weighted_total: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    overall_rating: Mapped[int] = mapped_column(Integer, default=3)
    recommendation: Mapped[str] = mapped_column(String(50), default="neutral")
    strengths: Mapped[list] = mapped_column(JSON, default=list)
    weaknesses: Mapped[list] = mapped_column(JSON, default=list)
    detailed_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_submitted: Mapped[bool] = mapped_column(default=False)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
