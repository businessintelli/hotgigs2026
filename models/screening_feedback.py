"""Screening feedback models — recruiter-level screening at application/import time."""

import enum
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, Enum, JSON, ForeignKey
from sqlalchemy.orm import relationship
from models.base import TenantBaseModel


# ── Enums ──────────────────────────────────────────────────

class ScreeningSource(str, enum.Enum):
    application = "application"          # candidate submitted application
    manual_import = "manual_import"      # recruiter added/imported
    resume_upload = "resume_upload"      # uploaded via bulk/email
    referral = "referral"                # referral pipeline
    ai_sourced = "ai_sourced"            # AI-powered sourcing
    job_board = "job_board"              # job-board apply


class ScreeningDecision(str, enum.Enum):
    proceed = "proceed"                  # move forward
    hold = "hold"                        # keep on hold
    reject = "reject"                    # rejected at screening
    shortlist = "shortlist"              # fast-tracked
    needs_review = "needs_review"        # escalate for senior review
    pending = "pending"                  # not yet screened


class ScreeningCategory(str, enum.Enum):
    skills_match = "skills_match"
    experience_level = "experience_level"
    work_authorization = "work_authorization"
    location_fit = "location_fit"
    rate_fit = "rate_fit"
    availability = "availability"
    communication = "communication"
    culture_fit = "culture_fit"
    education = "education"
    certifications = "certifications"
    references = "references"
    background = "background"
    overall = "overall"


class ScreeningQuestionType(str, enum.Enum):
    rating_1_5 = "rating_1_5"
    yes_no = "yes_no"
    select = "select"
    free_text = "free_text"
    checklist = "checklist"


# ── Models ─────────────────────────────────────────────────

class ScreeningChecklist(TenantBaseModel):
    """Configurable screening checklist template per organization."""
    __tablename__ = "screening_checklists"

    name = Column(String(200), nullable=False)
    description = Column(Text)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    applicable_to = Column(JSON, default=list)  # ["application", "manual_import", ...]
    items = relationship("ScreeningChecklistItem", back_populates="checklist", lazy="selectin")


class ScreeningChecklistItem(TenantBaseModel):
    """Individual item in a screening checklist."""
    __tablename__ = "screening_checklist_items"

    checklist_id = Column(Integer, ForeignKey("screening_checklists.id"), nullable=False)
    category = Column(Enum(ScreeningCategory), nullable=False)
    question_text = Column(String(500), nullable=False)
    question_type = Column(Enum(ScreeningQuestionType), default=ScreeningQuestionType.rating_1_5)
    options = Column(JSON, default=list)           # for select/checklist types
    weight = Column(Float, default=1.0)
    is_required = Column(Boolean, default=True)
    is_eliminatory = Column(Boolean, default=False)
    min_passing_score = Column(Integer, default=0)
    display_order = Column(Integer, default=0)
    help_text = Column(Text)

    checklist = relationship("ScreeningChecklist", back_populates="items")


class ScreeningFeedbackRecord(TenantBaseModel):
    """Screening feedback submitted by a recruiter for a candidate+requirement."""
    __tablename__ = "screening_feedback_records"

    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    requirement_id = Column(Integer, ForeignKey("requirements.id"), nullable=True)  # can be null for general screening
    checklist_id = Column(Integer, ForeignKey("screening_checklists.id"), nullable=True)
    screener_name = Column(String(200), nullable=False)
    screener_email = Column(String(200))
    screening_source = Column(Enum(ScreeningSource), nullable=False)

    # Computed scores
    overall_score = Column(Float, default=0)
    skills_score = Column(Float, default=0)
    experience_score = Column(Float, default=0)
    authorization_score = Column(Float, default=0)
    location_score = Column(Float, default=0)
    rate_score = Column(Float, default=0)
    availability_score = Column(Float, default=0)
    communication_score = Column(Float, default=0)

    # Decision
    decision = Column(Enum(ScreeningDecision), default=ScreeningDecision.pending)
    decision_reason = Column(Text)
    decision_at = Column(DateTime(timezone=True))

    # Notes
    summary_notes = Column(Text)
    strengths = Column(JSON, default=list)
    concerns = Column(JSON, default=list)
    red_flags = Column(JSON, default=list)

    # State
    is_draft = Column(Boolean, default=True)
    completed_at = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer)

    # Relationships
    answers = relationship("ScreeningAnswer", back_populates="feedback_record", lazy="selectin")


class ScreeningAnswer(TenantBaseModel):
    """Individual answer to a screening checklist item."""
    __tablename__ = "screening_answers"

    feedback_record_id = Column(Integer, ForeignKey("screening_feedback_records.id"), nullable=False)
    checklist_item_id = Column(Integer, ForeignKey("screening_checklist_items.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)

    # Answer data (polymorphic)
    answer_rating = Column(Integer)           # for rating_1_5
    answer_yes_no = Column(Boolean)           # for yes_no
    answer_choice = Column(String(500))       # for select
    answer_text = Column(Text)                # for free_text
    answer_checklist = Column(JSON, default=list)  # for checklist

    # Scoring
    score = Column(Float, default=0)          # normalized 0–100
    max_score = Column(Float, default=100)
    is_passing = Column(Boolean, default=True)
    evaluator_notes = Column(Text)

    feedback_record = relationship("ScreeningFeedbackRecord", back_populates="answers")
