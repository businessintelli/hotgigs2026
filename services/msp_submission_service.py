"""MSP Submission Service — manage the candidate submission pipeline."""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from models.organization import Organization
from models.candidate import Candidate
from models.msp_workflow import (
    RequirementDistribution, SupplierCandidateSubmission,
    MSPReview, ClientFeedback, PlacementRecord,
)
from models.enums import VMSSubmissionStatus, MSPReviewDecision, ClientFeedbackDecision, PlacementStatus

logger = logging.getLogger(__name__)


class MSPSubmissionService:
    """Manages the full candidate submission pipeline through VMS."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def submit_candidate(
        self,
        supplier_org_id: int,
        submitted_by_user_id: int,
        candidate_id: int,
        requirement_distribution_id: int,
        bill_rate: Optional[float] = None,
        pay_rate: Optional[float] = None,
        availability_date: Optional[Any] = None,
        supplier_notes: Optional[str] = None,
        candidate_summary: Optional[str] = None,
    ) -> SupplierCandidateSubmission:
        """Supplier submits a candidate for a distributed requirement."""
        # Verify distribution exists and is active
        dist_stmt = select(RequirementDistribution).where(
            RequirementDistribution.id == requirement_distribution_id,
            RequirementDistribution.supplier_org_id == supplier_org_id,
        )
        dist_result = await self.session.execute(dist_stmt)
        dist = dist_result.scalar_one_or_none()

        if not dist:
            raise ValueError("Distribution not found or not assigned to your organization")
        if dist.status != "ACTIVE":
            raise ValueError(f"Distribution is not active (status: {dist.status})")

        # Check submission limit
        count_stmt = select(func.count(SupplierCandidateSubmission.id)).where(
            SupplierCandidateSubmission.requirement_distribution_id == requirement_distribution_id,
            SupplierCandidateSubmission.organization_id == supplier_org_id,
        )
        count_result = await self.session.execute(count_stmt)
        current_count = count_result.scalar() or 0

        if current_count >= dist.max_submissions:
            raise ValueError(f"Submission limit reached ({dist.max_submissions})")

        # Check for duplicate candidate submission
        dup_stmt = select(SupplierCandidateSubmission).where(
            SupplierCandidateSubmission.requirement_distribution_id == requirement_distribution_id,
            SupplierCandidateSubmission.candidate_id == candidate_id,
        )
        dup_result = await self.session.execute(dup_stmt)
        if dup_result.scalar_one_or_none():
            raise ValueError("This candidate is already submitted for this requirement")

        submission = SupplierCandidateSubmission(
            organization_id=supplier_org_id,
            requirement_distribution_id=requirement_distribution_id,
            candidate_id=candidate_id,
            submitted_by_user_id=submitted_by_user_id,
            submitted_at=datetime.utcnow(),
            bill_rate=bill_rate,
            pay_rate=pay_rate,
            availability_date=availability_date,
            supplier_notes=supplier_notes,
            candidate_summary=candidate_summary,
            status=VMSSubmissionStatus.SUBMITTED,
        )
        self.session.add(submission)
        await self.session.commit()
        await self.session.refresh(submission)

        logger.info(f"Supplier {supplier_org_id} submitted candidate {candidate_id}")
        return submission

    async def review_submission(
        self,
        msp_org_id: int,
        submission_id: int,
        reviewer_id: int,
        decision: str,
        match_score: Optional[float] = None,
        quality_rating: Optional[int] = None,
        screening_notes: Optional[str] = None,
        strengths: Optional[str] = None,
        concerns: Optional[str] = None,
        recommendation: Optional[str] = None,
    ) -> MSPReview:
        """MSP recruiter reviews a supplier submission."""
        sub_stmt = select(SupplierCandidateSubmission).where(
            SupplierCandidateSubmission.id == submission_id
        )
        sub_result = await self.session.execute(sub_stmt)
        submission = sub_result.scalar_one_or_none()

        if not submission:
            raise ValueError(f"Submission {submission_id} not found")

        # Update submission status
        if decision == MSPReviewDecision.APPROVE or decision == "approve":
            submission.status = VMSSubmissionStatus.MSP_APPROVED
        elif decision == MSPReviewDecision.REJECT or decision == "reject":
            submission.status = VMSSubmissionStatus.MSP_REJECTED
        elif decision == MSPReviewDecision.REQUEST_CHANGES or decision == "request_changes":
            submission.status = VMSSubmissionStatus.CHANGES_REQUESTED

        # Create review record
        review = MSPReview(
            supplier_submission_id=submission_id,
            organization_id=msp_org_id,
            reviewer_id=reviewer_id,
            reviewed_at=datetime.utcnow(),
            decision=decision,
            match_score=match_score,
            quality_rating=quality_rating,
            screening_notes=screening_notes,
            strengths=strengths,
            concerns=concerns,
            recommendation=recommendation,
        )
        self.session.add(review)
        await self.session.commit()
        await self.session.refresh(review)

        logger.info(f"MSP reviewed submission {submission_id}: {decision}")
        return review

    async def forward_to_client(
        self,
        submission_id: int,
        client_package_notes: Optional[str] = None,
    ) -> SupplierCandidateSubmission:
        """Forward an approved submission to the client."""
        sub_stmt = select(SupplierCandidateSubmission).where(
            SupplierCandidateSubmission.id == submission_id
        )
        sub_result = await self.session.execute(sub_stmt)
        submission = sub_result.scalar_one_or_none()

        if not submission:
            raise ValueError(f"Submission {submission_id} not found")

        submission.status = VMSSubmissionStatus.SUBMITTED_TO_CLIENT

        # Update the latest MSP review with forward timestamp
        review_stmt = select(MSPReview).where(
            MSPReview.supplier_submission_id == submission_id,
        ).order_by(MSPReview.reviewed_at.desc()).limit(1)
        review_result = await self.session.execute(review_stmt)
        review = review_result.scalar_one_or_none()

        if review:
            review.forwarded_to_client_at = datetime.utcnow()
            if client_package_notes:
                review.client_package_notes = client_package_notes

        await self.session.commit()
        logger.info(f"Forwarded submission {submission_id} to client")
        return submission

    async def record_client_feedback(
        self,
        submission_id: int,
        client_org_id: int,
        client_user_id: int,
        decision: str,
        feedback_notes: Optional[str] = None,
        rating: Optional[int] = None,
        preferred_interview_date: Optional[datetime] = None,
        interview_type: Optional[str] = None,
    ) -> ClientFeedback:
        """Record client's feedback on a submitted candidate."""
        sub_stmt = select(SupplierCandidateSubmission).where(
            SupplierCandidateSubmission.id == submission_id
        )
        sub_result = await self.session.execute(sub_stmt)
        submission = sub_result.scalar_one_or_none()

        if not submission:
            raise ValueError(f"Submission {submission_id} not found")

        # Update submission status based on client decision
        if decision == "shortlist":
            submission.status = VMSSubmissionStatus.CLIENT_SHORTLISTED
        elif decision == "reject":
            submission.status = VMSSubmissionStatus.CLIENT_REJECTED
        elif decision == "interview":
            submission.status = VMSSubmissionStatus.INTERVIEW

        feedback = ClientFeedback(
            supplier_submission_id=submission_id,
            client_org_id=client_org_id,
            client_user_id=client_user_id,
            feedback_at=datetime.utcnow(),
            decision=decision,
            feedback_notes=feedback_notes,
            rating=rating,
            preferred_interview_date=preferred_interview_date,
            interview_type=interview_type,
        )
        self.session.add(feedback)
        await self.session.commit()
        await self.session.refresh(feedback)

        logger.info(f"Client feedback on submission {submission_id}: {decision}")
        return feedback

    async def get_submission_pipeline(
        self, requirement_id: Optional[int] = None, msp_org_id: Optional[int] = None,
        status_filter: Optional[str] = None, offset: int = 0, limit: int = 50,
    ) -> Dict[str, Any]:
        """Get the full submission pipeline with enriched data."""
        stmt = select(SupplierCandidateSubmission)

        if requirement_id:
            stmt = stmt.join(RequirementDistribution).where(
                RequirementDistribution.requirement_id == requirement_id
            )
        if msp_org_id:
            stmt = stmt.join(
                RequirementDistribution,
                RequirementDistribution.id == SupplierCandidateSubmission.requirement_distribution_id,
            ).where(RequirementDistribution.organization_id == msp_org_id)
        if status_filter:
            stmt = stmt.where(SupplierCandidateSubmission.status == status_filter)

        # Count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        # Fetch
        stmt = stmt.order_by(SupplierCandidateSubmission.submitted_at.desc())
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        submissions = list(result.scalars().all())

        return {
            "items": submissions,
            "total": total,
            "offset": offset,
            "limit": limit,
        }

    async def get_supplier_submissions(
        self, supplier_org_id: int, status_filter: Optional[str] = None,
        offset: int = 0, limit: int = 50,
    ) -> Dict[str, Any]:
        """Get submissions by a specific supplier."""
        stmt = select(SupplierCandidateSubmission).where(
            SupplierCandidateSubmission.organization_id == supplier_org_id,
        )
        if status_filter:
            stmt = stmt.where(SupplierCandidateSubmission.status == status_filter)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        stmt = stmt.order_by(SupplierCandidateSubmission.submitted_at.desc())
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        submissions = list(result.scalars().all())

        return {
            "items": submissions,
            "total": total,
            "offset": offset,
            "limit": limit,
        }
