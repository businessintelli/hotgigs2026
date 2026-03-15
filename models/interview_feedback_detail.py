"""Detailed Interview Feedback Models — structured Q&A questionnaires,
persistent candidate technology scores, recruiter visibility controls,
and score-to-job computation for long-term matching intelligence.

Extends the basic InterviewFeedback model with:
- Configurable question banks (technical + non-technical)
- Per-question answer collection with scoring
- Persistent candidate skill/tech scores aggregated across interviews
- Recruiter-controlled visibility flags for submission sharing
- Score computation against specific job requirements
"""
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, Enum, JSON
)
from sqlalchemy.orm import relationship
import enum

from models.base import BaseModel


# ──────────────────────────────────────────────────────────
#  ENUMS
# ──────────────────────────────────────────────────────────

class QuestionCategory(str, enum.Enum):
    """Categories for structured interview questions."""
    technical = "technical"
    framework = "framework"
    architecture = "architecture"
    coding = "coding"
    system_design = "system_design"
    immigration = "immigration"
    location = "location"
    availability = "availability"
    compensation = "compensation"
    work_authorization = "work_authorization"
    relocation = "relocation"
    references = "references"
    background = "background"
    culture_fit = "culture_fit"
    communication = "communication"
    leadership = "leadership"
    project_experience = "project_experience"
    certifications = "certifications"
    custom = "custom"


class QuestionType(str, enum.Enum):
    """How the question is answered."""
    rating_1_5 = "rating_1_5"
    rating_1_10 = "rating_1_10"
    yes_no = "yes_no"
    multiple_choice = "multiple_choice"
    free_text = "free_text"
    numeric = "numeric"
    date = "date"
    select = "select"


class FeedbackSource(str, enum.Enum):
    """Who conducted the interview."""
    recruiter = "recruiter"
    ai_bot = "ai_bot"
    hiring_manager = "hiring_manager"
    technical_panel = "technical_panel"
    client = "client"
    vendor = "vendor"


class VisibilityLevel(str, enum.Enum):
    """Who can see this feedback."""
    internal_only = "internal_only"
    share_with_client = "share_with_client"
    share_with_supplier = "share_with_supplier"
    share_with_candidate = "share_with_candidate"
    public = "public"


class ScoreStatus(str, enum.Enum):
    """Status of a persistent score."""
    active = "active"
    expired = "expired"
    superseded = "superseded"


# ──────────────────────────────────────────────────────────
#  QUESTION BANK — Configurable question templates
# ──────────────────────────────────────────────────────────

class InterviewQuestionBank(BaseModel):
    """Reusable question templates organized by category and technology."""
    __tablename__ = "interview_question_bank"

    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    question_text = Column(Text, nullable=False)
    category = Column(Enum(QuestionCategory), nullable=False, index=True)
    question_type = Column(Enum(QuestionType), nullable=False, default=QuestionType.rating_1_5)
    technology = Column(String(100), nullable=True, index=True)  # e.g. "Python", "AWS", "React"
    skill_tag = Column(String(100), nullable=True, index=True)   # e.g. "backend", "devops", "visa"
    difficulty_level = Column(String(20), nullable=True)  # easy, medium, hard, expert
    options = Column(JSON, nullable=True)  # For multiple_choice / select types
    expected_answer = Column(Text, nullable=True)  # Reference answer for evaluators
    scoring_guide = Column(JSON, nullable=True)  # { "1": "No knowledge", "3": "Working knowledge", "5": "Expert" }
    weight = Column(Float, default=1.0)  # Weight when computing aggregate score
    is_required = Column(Boolean, default=False)
    is_eliminatory = Column(Boolean, default=False)  # Failing = automatic disqualification
    min_passing_score = Column(Float, nullable=True)  # Minimum acceptable score
    is_active = Column(Boolean, default=True)
    is_global = Column(Boolean, default=True)  # Available to all orgs or org-specific
    tags = Column(JSON, nullable=True)  # Additional tags for filtering
    usage_count = Column(Integer, default=0)

    # Relationships
    answers = relationship("InterviewQuestionAnswer", back_populates="question", cascade="all, delete-orphan")


# ──────────────────────────────────────────────────────────
#  DETAILED FEEDBACK SESSION — One per interview
# ──────────────────────────────────────────────────────────

class DetailedFeedbackSession(BaseModel):
    """A complete feedback session for one interview, collecting structured Q&A."""
    __tablename__ = "detailed_feedback_sessions"

    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id"), nullable=True, index=True)
    evaluator_name = Column(String(200), nullable=False)
    evaluator_email = Column(String(200), nullable=True)
    feedback_source = Column(Enum(FeedbackSource), nullable=False, default=FeedbackSource.recruiter)

    # Overall assessment
    overall_rating = Column(Float, nullable=True)  # Computed from individual answers
    overall_recommendation = Column(String(30), nullable=True)  # strong_hire, hire, maybe, no_hire, strong_no_hire
    summary_notes = Column(Text, nullable=True)
    strengths = Column(JSON, nullable=True)  # List of identified strengths
    concerns = Column(JSON, nullable=True)   # List of concerns/red flags

    # Computed scores by category
    technical_score = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)
    culture_fit_score = Column(Float, nullable=True)
    immigration_score = Column(Float, nullable=True)
    location_score = Column(Float, nullable=True)
    availability_score = Column(Float, nullable=True)

    # Job-specific scoring
    job_fit_score = Column(Float, nullable=True)  # How well candidate matches THIS specific job
    technology_match_score = Column(Float, nullable=True)  # Score against required technologies

    # Visibility & sharing controls (recruiter decides)
    visibility = Column(Enum(VisibilityLevel), default=VisibilityLevel.internal_only)
    share_technical_scores = Column(Boolean, default=True)
    share_immigration_details = Column(Boolean, default=False)
    share_compensation_details = Column(Boolean, default=False)
    share_detailed_notes = Column(Boolean, default=False)
    shared_with_submission = Column(Boolean, default=False)  # Attached to a submission?

    # Metadata
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    is_draft = Column(Boolean, default=True)

    # Relationships
    answers = relationship("InterviewQuestionAnswer", back_populates="feedback_session", cascade="all, delete-orphan")


# ──────────────────────────────────────────────────────────
#  QUESTION ANSWERS — Individual responses within a session
# ──────────────────────────────────────────────────────────

class InterviewQuestionAnswer(BaseModel):
    """Individual answer to a question within a feedback session."""
    __tablename__ = "interview_question_answers"

    feedback_session_id = Column(Integer, ForeignKey("detailed_feedback_sessions.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("interview_question_bank.id"), nullable=False, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)

    # Answer data (polymorphic based on question type)
    answer_text = Column(Text, nullable=True)      # For free_text
    answer_rating = Column(Float, nullable=True)    # For rating types
    answer_choice = Column(String(200), nullable=True)  # For multiple_choice / yes_no / select
    answer_numeric = Column(Float, nullable=True)   # For numeric
    answer_date = Column(DateTime, nullable=True)   # For date

    # Scoring
    score = Column(Float, nullable=True)  # Normalized 0-100
    max_score = Column(Float, default=100.0)
    evaluator_notes = Column(Text, nullable=True)
    is_passing = Column(Boolean, nullable=True)  # Met minimum threshold?

    # Relationships
    feedback_session = relationship("DetailedFeedbackSession", back_populates="answers")
    question = relationship("InterviewQuestionBank", back_populates="answers")


# ──────────────────────────────────────────────────────────
#  PERSISTENT CANDIDATE SCORES — Accumulated over time
# ──────────────────────────────────────────────────────────

class CandidatePersistentScore(BaseModel):
    """Aggregated score for a candidate on a specific skill/technology,
    accumulated across multiple interviews over time. Used for
    future job matching and recommendations."""
    __tablename__ = "candidate_persistent_scores"

    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    skill_or_technology = Column(String(100), nullable=False, index=True)  # e.g. "Python", "AWS", "React", "immigration_h1b"
    category = Column(Enum(QuestionCategory), nullable=False)

    # Aggregated score
    current_score = Column(Float, nullable=False, default=0.0)  # 0-100
    score_count = Column(Integer, default=0)  # Number of assessments contributing
    score_sum = Column(Float, default=0.0)    # Running sum for average calculation
    highest_score = Column(Float, default=0.0)
    lowest_score = Column(Float, default=100.0)
    last_assessed_at = Column(DateTime, nullable=True)
    last_interview_id = Column(Integer, nullable=True)

    # Confidence & trend
    confidence_level = Column(Float, default=0.0)  # 0-1, increases with more assessments
    trend = Column(String(20), nullable=True)  # improving, stable, declining
    score_history = Column(JSON, nullable=True)  # [{date, score, interview_id}, ...]

    # Status
    status = Column(Enum(ScoreStatus), default=ScoreStatus.active)
    expires_at = Column(DateTime, nullable=True)  # Some scores may expire (e.g. certifications)


# ──────────────────────────────────────────────────────────
#  JOB MATCH SCORE — Feedback scores computed against a job
# ──────────────────────────────────────────────────────────

class CandidateJobMatchScore(BaseModel):
    """Computed score of a candidate against a specific job requirement,
    derived from interview feedback and persistent scores."""
    __tablename__ = "candidate_job_match_scores"

    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id"), nullable=False, index=True)

    # Composite scores
    overall_match_score = Column(Float, nullable=False, default=0.0)  # 0-100
    technical_match_score = Column(Float, nullable=True)
    experience_match_score = Column(Float, nullable=True)
    immigration_match_score = Column(Float, nullable=True)
    location_match_score = Column(Float, nullable=True)
    availability_match_score = Column(Float, nullable=True)
    culture_match_score = Column(Float, nullable=True)
    compensation_match_score = Column(Float, nullable=True)

    # Breakdown
    matched_skills = Column(JSON, nullable=True)    # [{skill, required_level, candidate_level, gap}, ...]
    missing_skills = Column(JSON, nullable=True)     # [skill, ...]
    exceeding_skills = Column(JSON, nullable=True)   # Skills above requirement
    risk_factors = Column(JSON, nullable=True)       # Immigration, relocation, etc.
    recommendation = Column(String(50), nullable=True)  # strong_fit, good_fit, partial_fit, poor_fit

    # Source tracking
    feedback_sessions_used = Column(JSON, nullable=True)  # IDs of feedback sessions used
    persistent_scores_used = Column(JSON, nullable=True)  # IDs of persistent scores used
    computed_at = Column(DateTime, default=datetime.utcnow)
    is_stale = Column(Boolean, default=False)  # Needs recomputation?
