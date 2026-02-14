"""Resume harvesting data models."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, DateTime, Boolean, Float, Text, JSON, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel


class HarvestSource(BaseModel):
    """Data source configuration for candidate harvesting."""

    __tablename__ = "harvest_sources"
    __table_args__ = (
        Index("ix_harvest_sources_name", "name"),
        Index("ix_harvest_sources_source_type", "source_type"),
        Index("ix_harvest_sources_is_active", "is_active"),
    )

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # job_board/social/developer_community/forum
    api_endpoint: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    api_key_encrypted: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    api_secret_encrypted: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    rate_limit_per_hour: Mapped[int] = mapped_column(Integer, default=100)
    rate_limit_per_day: Mapped[int] = mapped_column(Integer, default=1000)
    config: Mapped[Dict[str, Any]] = mapped_column(JSON, default={}, nullable=False)
    last_harvested_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    total_candidates_harvested: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    jobs: Mapped[List["HarvestJob"]] = relationship("HarvestJob", back_populates="source")
    results: Mapped[List["HarvestResult"]] = relationship("HarvestResult", back_populates="source")


class HarvestJob(BaseModel):
    """Harvest job configuration and execution tracking."""

    __tablename__ = "harvest_jobs"
    __table_args__ = (
        Index("ix_harvest_jobs_source_id", "source_id"),
        Index("ix_harvest_jobs_status", "status"),
        Index("ix_harvest_jobs_next_run_at", "next_run_at"),
    )

    source_id: Mapped[int] = mapped_column(ForeignKey("harvest_sources.id"), nullable=False)
    search_criteria: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    frequency: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # once/daily/weekly/monthly
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending/running/completed/failed/scheduled
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    candidates_found: Mapped[int] = mapped_column(Integer, default=0)
    candidates_new: Mapped[int] = mapped_column(Integer, default=0)
    candidates_updated: Mapped[int] = mapped_column(Integer, default=0)
    candidates_duplicate: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    next_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Relationships
    source: Mapped["HarvestSource"] = relationship("HarvestSource", back_populates="jobs")
    results: Mapped[List["HarvestResult"]] = relationship("HarvestResult", back_populates="job")


class HarvestResult(BaseModel):
    """Individual harvest result for a candidate."""

    __tablename__ = "harvest_results"
    __table_args__ = (
        Index("ix_harvest_results_job_id", "job_id"),
        Index("ix_harvest_results_source_id", "source_id"),
        Index("ix_harvest_results_candidate_id", "candidate_id"),
        Index("ix_harvest_results_status", "status"),
    )

    job_id: Mapped[int] = mapped_column(ForeignKey("harvest_jobs.id"), nullable=False)
    source_id: Mapped[int] = mapped_column(ForeignKey("harvest_sources.id"), nullable=False)
    candidate_id: Mapped[Optional[int]] = mapped_column(ForeignKey("candidates.id"), nullable=True)
    raw_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    source_profile_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_profile_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="raw")  # raw/processed/duplicate/error
    match_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    job: Mapped["HarvestJob"] = relationship("HarvestJob", back_populates="results")
    source: Mapped["HarvestSource"] = relationship("HarvestSource", back_populates="results")


class CandidateSourceMapping(BaseModel):
    """Cross-reference mapping of candidates to harvest sources."""

    __tablename__ = "candidate_source_mappings"
    __table_args__ = (
        Index("ix_candidate_source_mappings_candidate_id", "candidate_id"),
        Index("ix_candidate_source_mappings_source_id", "source_id"),
        UniqueConstraint("candidate_id", "source_id", name="uq_candidate_source"),
    )

    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False)
    source_id: Mapped[int] = mapped_column(ForeignKey("harvest_sources.id"), nullable=False)
    source_profile_id: Mapped[str] = mapped_column(String(255), nullable=False)
    source_profile_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
