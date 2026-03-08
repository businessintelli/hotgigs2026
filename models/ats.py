from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, Boolean, DateTime, Date, JSON, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel
from models.enums import (
    JobOrderPriority,
    JobOrderDistribution,
    JobOrderStatus,
    OfferStatus,
    OnboardingTaskType,
    OnboardingTaskStatus,
    InterviewRecommendation,
)


class JobOrder(BaseModel):
    """Enhanced job requisition tracking."""

    __tablename__ = "job_orders"

    requirement_id: Mapped[int] = mapped_column(ForeignKey("requirements.id"), nullable=False, index=True)
    client_org_id: Mapped[Optional[int]] = mapped_column(ForeignKey("organizations.id"))
    priority: Mapped[str] = mapped_column(
        Enum(JobOrderPriority),
        default=JobOrderPriority.NORMAL,
        nullable=False,
    )
    target_fill_date: Mapped[Optional[date]] = mapped_column(Date)
    max_submissions: Mapped[int] = mapped_column(Integer, default=5)
    distribution_type: Mapped[str] = mapped_column(
        Enum(JobOrderDistribution),
        default=JobOrderDistribution.OPEN,
        nullable=False,
    )
    distributed_to: Mapped[Optional[list]] = mapped_column(
        JSON,
        default=list,
        comment="List of supplier organization IDs",
    )
    status: Mapped[str] = mapped_column(
        Enum(JobOrderStatus),
        default=JobOrderStatus.DRAFT,
        nullable=False,
        index=True,
    )
    filled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    cancelled_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    requirement = relationship("Requirement", foreign_keys=[requirement_id])
    client_org = relationship("Organization", foreign_keys=[client_org_id])

    def __repr__(self) -> str:
        return f"<JobOrder(id={self.id}, requirement_id={self.requirement_id}, status={self.status})>"


class OfferWorkflow(BaseModel):
    """Offer management workflow."""

    __tablename__ = "offer_workflows"

    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id"), nullable=False, index=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    offer_status: Mapped[str] = mapped_column(
        Enum(OfferStatus),
        default=OfferStatus.DRAFT,
        nullable=False,
        index=True,
    )
    bill_rate: Mapped[Optional[float]] = mapped_column(Float)
    pay_rate: Mapped[Optional[float]] = mapped_column(Float)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    benefits_package: Mapped[Optional[str]] = mapped_column(Text)
    approved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    extended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    decline_reason: Mapped[Optional[str]] = mapped_column(Text)
    counter_offer_details: Mapped[Optional[dict]] = mapped_column(JSON)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)

    # Relationships
    submission = relationship("Submission", foreign_keys=[submission_id])
    candidate = relationship("Candidate", foreign_keys=[candidate_id])
    approved_by_user = relationship("User", foreign_keys=[approved_by])

    def __repr__(self) -> str:
        return f"<OfferWorkflow(id={self.id}, candidate_id={self.candidate_id}, status={self.offer_status})>"


class OnboardingTask(BaseModel):
    """Post-offer onboarding tracking."""

    __tablename__ = "onboarding_tasks"

    placement_id: Mapped[Optional[int]] = mapped_column(ForeignKey("placement_records.id"))
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    task_name: Mapped[str] = mapped_column(String(255), nullable=False)
    task_type: Mapped[str] = mapped_column(
        Enum(OnboardingTaskType),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        Enum(OnboardingTaskStatus),
        default=OnboardingTaskStatus.PENDING,
        nullable=False,
        index=True,
    )
    assigned_to: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    candidate = relationship("Candidate", foreign_keys=[candidate_id])
    assigned_to_user = relationship("User", foreign_keys=[assigned_to])

    def __repr__(self) -> str:
        return f"<OnboardingTask(id={self.id}, candidate_id={self.candidate_id}, type={self.task_type})>"


class InterviewFeedback(BaseModel):
    """Structured interview feedback."""

    __tablename__ = "structured_interview_feedbacks"

    interview_id: Mapped[Optional[int]] = mapped_column(ForeignKey("interviews.id"))
    submission_id: Mapped[Optional[int]] = mapped_column(ForeignKey("submissions.id"))
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    interviewer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    overall_rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    technical_score: Mapped[Optional[int]] = mapped_column(Integer)  # 0-100
    communication_score: Mapped[Optional[int]] = mapped_column(Integer)  # 0-100
    culture_fit_score: Mapped[Optional[int]] = mapped_column(Integer)  # 0-100
    problem_solving_score: Mapped[Optional[int]] = mapped_column(Integer)  # 0-100
    strengths: Mapped[Optional[str]] = mapped_column(Text)
    weaknesses: Mapped[Optional[str]] = mapped_column(Text)
    recommendation: Mapped[str] = mapped_column(
        Enum(InterviewRecommendation),
        nullable=False,
    )
    detailed_notes: Mapped[Optional[str]] = mapped_column(Text)
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    interview = relationship("Interview", foreign_keys=[interview_id])
    submission = relationship("Submission", foreign_keys=[submission_id])
    candidate = relationship("Candidate", foreign_keys=[candidate_id])
    interviewer = relationship("User", foreign_keys=[interviewer_id])

    def __repr__(self) -> str:
        return f"<InterviewFeedback(id={self.id}, candidate_id={self.candidate_id}, recommendation={self.recommendation})>"
