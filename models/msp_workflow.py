"""VMS/MSP workflow models — requirement distribution, submissions, reviews, placements."""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    String, DateTime, Date, Enum, JSON, ForeignKey, Text, Float, Integer,
    Index, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel
from models.enums import (
    DistributionStatus, VMSSubmissionStatus, MSPReviewDecision,
    ClientFeedbackDecision, PlacementStatus, TimesheetFrequency,
)


class RequirementDistribution(BaseModel):
    """
    MSP distributes a client's requirement to selected suppliers.
    Each row = one requirement shared with one supplier.
    Inspired by Beeline/Fieldglass VMS distribution model.
    """

    __tablename__ = "requirement_distributions"

    # MSP that owns this distribution
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    # The requirement being shared
    requirement_id: Mapped[int] = mapped_column(
        ForeignKey("requirements.id"), nullable=False, index=True
    )
    # The supplier receiving this requirement
    supplier_org_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    # Distribution metadata
    distributed_by_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    distributed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(
        Enum(DistributionStatus),
        default=DistributionStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    max_submissions: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    notes_to_supplier: Mapped[Optional[str]] = mapped_column(Text)
    supplier_response_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    supplier_declined_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    msp_organization = relationship("Organization", foreign_keys=[organization_id])
    supplier_organization = relationship("Organization", foreign_keys=[supplier_org_id])
    requirement = relationship("Requirement", backref="distributions")
    distributed_by = relationship("User")

    __table_args__ = (
        Index("ix_dist_req_supplier", "requirement_id", "supplier_org_id", unique=True),
        Index("ix_dist_supplier_status", "supplier_org_id", "status"),
        Index("ix_dist_org_status", "organization_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<ReqDistribution(req={self.requirement_id}, supplier_org={self.supplier_org_id})>"


class SupplierCandidateSubmission(BaseModel):
    """
    Supplier submits a candidate for a distributed requirement.
    This goes through MSP review before reaching the client.
    """

    __tablename__ = "supplier_candidate_submissions"

    # Supplier org that submitted
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    # Which distribution this is for
    requirement_distribution_id: Mapped[int] = mapped_column(
        ForeignKey("requirement_distributions.id"), nullable=False, index=True
    )
    # The candidate being submitted
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"), nullable=False, index=True
    )
    # Submitted by which user
    submitted_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Rate info
    bill_rate: Mapped[Optional[float]] = mapped_column(Float)
    pay_rate: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)

    # Candidate info
    availability_date: Mapped[Optional[date]] = mapped_column(Date)
    supplier_notes: Mapped[Optional[str]] = mapped_column(Text)
    candidate_summary: Mapped[Optional[str]] = mapped_column(Text)

    # Pipeline status
    status: Mapped[str] = mapped_column(
        Enum(VMSSubmissionStatus),
        default=VMSSubmissionStatus.SUBMITTED,
        nullable=False,
        index=True,
    )

    # AI-computed scores
    quality_score: Mapped[Optional[float]] = mapped_column(Float)
    match_score: Mapped[Optional[float]] = mapped_column(Float)
    duplicate_flag: Mapped[Optional[str]] = mapped_column(String(50))  # UNIQUE, POTENTIAL_DUPLICATE, CONFIRMED_DUPLICATE

    # Relationships
    supplier_organization = relationship("Organization", foreign_keys=[organization_id])
    distribution = relationship("RequirementDistribution", backref="submissions")
    candidate = relationship("Candidate", backref="vms_submissions")
    submitted_by = relationship("User")

    __table_args__ = (
        Index("ix_sub_dist_candidate", "requirement_distribution_id", "candidate_id", unique=True),
        Index("ix_sub_org_status", "organization_id", "status"),
        Index("ix_sub_status_created", "status", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<SupplierSubmission(id={self.id}, candidate={self.candidate_id}, status={self.status})>"


class MSPReview(BaseModel):
    """MSP recruiter's review of a supplier-submitted candidate."""

    __tablename__ = "msp_reviews"

    # Link to supplier submission
    supplier_submission_id: Mapped[int] = mapped_column(
        ForeignKey("supplier_candidate_submissions.id"), nullable=False, index=True
    )
    # MSP org
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    # Reviewer (MSP recruiter)
    reviewer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Decision
    decision: Mapped[str] = mapped_column(
        Enum(MSPReviewDecision), nullable=False
    )
    match_score: Mapped[Optional[float]] = mapped_column(Float)
    quality_rating: Mapped[Optional[int]] = mapped_column(Integer)  # 1-5

    # Detailed notes
    screening_notes: Mapped[Optional[str]] = mapped_column(Text)
    strengths: Mapped[Optional[str]] = mapped_column(Text)
    concerns: Mapped[Optional[str]] = mapped_column(Text)
    recommendation: Mapped[Optional[str]] = mapped_column(Text)

    # Forwarded to client
    forwarded_to_client_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    client_package_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    supplier_submission = relationship("SupplierCandidateSubmission", backref="msp_reviews")
    msp_organization = relationship("Organization")
    reviewer = relationship("User")

    __table_args__ = (
        Index("ix_review_submission", "supplier_submission_id"),
        Index("ix_review_org_date", "organization_id", "reviewed_at"),
    )

    def __repr__(self) -> str:
        return f"<MSPReview(submission={self.supplier_submission_id}, decision={self.decision})>"


class ClientFeedback(BaseModel):
    """Client's feedback on a candidate submitted by MSP."""

    __tablename__ = "client_feedbacks"

    # Link to supplier submission (which was forwarded to client)
    supplier_submission_id: Mapped[int] = mapped_column(
        ForeignKey("supplier_candidate_submissions.id"), nullable=False, index=True
    )
    # Client org
    client_org_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    # Client user providing feedback
    client_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    feedback_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Decision
    decision: Mapped[str] = mapped_column(
        Enum(ClientFeedbackDecision), nullable=False
    )
    feedback_notes: Mapped[Optional[str]] = mapped_column(Text)
    rating: Mapped[Optional[int]] = mapped_column(Integer)  # 1-5

    # Interview scheduling (if decision = INTERVIEW)
    preferred_interview_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    interview_type: Mapped[Optional[str]] = mapped_column(String(50))

    # Relationships
    supplier_submission = relationship("SupplierCandidateSubmission", backref="client_feedbacks")
    client_organization = relationship("Organization")
    client_user = relationship("User")

    __table_args__ = (
        Index("ix_feedback_submission", "supplier_submission_id"),
        Index("ix_feedback_client_date", "client_org_id", "feedback_at"),
    )

    def __repr__(self) -> str:
        return f"<ClientFeedback(submission={self.supplier_submission_id}, decision={self.decision})>"


class PlacementRecord(BaseModel):
    """
    Records a successful placement — candidate placed at client through MSP.
    Tracks billing, timesheets, and placement lifecycle.
    """

    __tablename__ = "placement_records"

    # MSP org managing the placement
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    # Parties
    requirement_id: Mapped[int] = mapped_column(
        ForeignKey("requirements.id"), nullable=False, index=True
    )
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"), nullable=False, index=True
    )
    supplier_org_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    client_org_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    supplier_submission_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("supplier_candidate_submissions.id"), nullable=True
    )

    # Placement details
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    bill_rate: Mapped[float] = mapped_column(Float, nullable=False)
    pay_rate: Mapped[float] = mapped_column(Float, nullable=False)
    msp_margin: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)

    # Status
    status: Mapped[str] = mapped_column(
        Enum(PlacementStatus),
        default=PlacementStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    timesheet_frequency: Mapped[str] = mapped_column(
        Enum(TimesheetFrequency),
        default=TimesheetFrequency.WEEKLY,
        nullable=False,
    )

    # Work details
    work_location: Mapped[Optional[str]] = mapped_column(String(255))
    job_title: Mapped[Optional[str]] = mapped_column(String(200))
    department: Mapped[Optional[str]] = mapped_column(String(100))
    manager_name: Mapped[Optional[str]] = mapped_column(String(200))
    manager_email: Mapped[Optional[str]] = mapped_column(String(255))

    # Termination/extension
    terminated_at: Mapped[Optional[date]] = mapped_column(Date)
    termination_reason: Mapped[Optional[str]] = mapped_column(Text)
    extended_end_date: Mapped[Optional[date]] = mapped_column(Date)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    msp_organization = relationship("Organization", foreign_keys=[organization_id])
    supplier_organization = relationship("Organization", foreign_keys=[supplier_org_id])
    client_organization = relationship("Organization", foreign_keys=[client_org_id])
    requirement = relationship("Requirement", backref="placements")
    candidate = relationship("Candidate", backref="placements")
    supplier_submission = relationship("SupplierCandidateSubmission", backref="placement")

    __table_args__ = (
        Index("ix_placement_msp_status", "organization_id", "status"),
        Index("ix_placement_client", "client_org_id", "status"),
        Index("ix_placement_supplier", "supplier_org_id", "status"),
        Index("ix_placement_candidate", "candidate_id"),
    )

    def __repr__(self) -> str:
        return f"<Placement(id={self.id}, candidate={self.candidate_id}, status={self.status})>"
