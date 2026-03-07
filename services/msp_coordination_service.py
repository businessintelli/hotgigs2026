"""MSP Coordination Service — orchestrates the VMS workflow lifecycle with SLA tracking."""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from models.msp_workflow import (
    RequirementDistribution, SupplierCandidateSubmission,
    MSPReview, ClientFeedback, PlacementRecord,
)
from models.organization import Organization
from models.requirement import Requirement
from models.enums import (
    VMSSubmissionStatus, DistributionStatus, PlacementStatus,
    MSPReviewDecision, ClientFeedbackDecision,
)

logger = logging.getLogger(__name__)


# Default SLA thresholds (in hours)
DEFAULT_SLAS = {
    "supplier_response": 48,      # Hours for supplier to respond/submit
    "msp_review": 24,             # Hours for MSP to review submission
    "client_feedback": 72,        # Hours for client to provide feedback
    "interview_scheduling": 48,   # Hours to schedule interview after shortlist
}


class MSPCoordinationService:
    """Orchestrates the full VMS workflow lifecycle."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_workflow_status(self, requirement_id: int) -> Dict[str, Any]:
        """Get comprehensive workflow status for a requirement."""
        # Get distributions
        dist_stmt = select(RequirementDistribution).where(
            RequirementDistribution.requirement_id == requirement_id
        )
        dist_result = await self.session.execute(dist_stmt)
        distributions = list(dist_result.scalars().all())

        # Get all submissions across distributions
        dist_ids = [d.id for d in distributions]
        submissions = []
        if dist_ids:
            sub_stmt = select(SupplierCandidateSubmission).where(
                SupplierCandidateSubmission.requirement_distribution_id.in_(dist_ids)
            )
            sub_result = await self.session.execute(sub_stmt)
            submissions = list(sub_result.scalars().all())

        # Pipeline counts
        pipeline = {
            "submitted": 0,
            "under_msp_review": 0,
            "msp_approved": 0,
            "msp_rejected": 0,
            "submitted_to_client": 0,
            "client_shortlisted": 0,
            "client_rejected": 0,
            "interview": 0,
            "offer": 0,
            "placed": 0,
            "withdrawn": 0,
        }
        for sub in submissions:
            status_key = str(sub.status).lower().replace("vmssub", "")
            if hasattr(VMSSubmissionStatus, str(sub.status).split(".")[-1] if "." in str(sub.status) else str(sub.status)):
                key = str(sub.status).split(".")[-1].lower() if "." in str(sub.status) else str(sub.status).lower()
                if key in pipeline:
                    pipeline[key] += 1

        return {
            "requirement_id": requirement_id,
            "total_distributions": len(distributions),
            "active_distributions": sum(1 for d in distributions if str(d.status) == "ACTIVE" or d.status == DistributionStatus.ACTIVE),
            "total_submissions": len(submissions),
            "pipeline": pipeline,
        }

    async def check_sla_breaches(self, msp_org_id: int) -> List[Dict[str, Any]]:
        """Check for SLA breaches across all active workflows."""
        breaches = []
        now = datetime.utcnow()

        # 1. Supplier response SLA — distributions with no submissions past deadline
        dist_stmt = select(RequirementDistribution).where(
            RequirementDistribution.organization_id == msp_org_id,
            RequirementDistribution.status == DistributionStatus.ACTIVE,
        )
        dist_result = await self.session.execute(dist_stmt)
        distributions = list(dist_result.scalars().all())

        for dist in distributions:
            hours_since = (now - dist.distributed_at.replace(tzinfo=None)).total_seconds() / 3600
            if hours_since > DEFAULT_SLAS["supplier_response"]:
                # Check if any submissions exist
                count_stmt = select(func.count(SupplierCandidateSubmission.id)).where(
                    SupplierCandidateSubmission.requirement_distribution_id == dist.id
                )
                count_result = await self.session.execute(count_stmt)
                if (count_result.scalar() or 0) == 0:
                    breaches.append({
                        "type": "supplier_response",
                        "entity_id": dist.id,
                        "entity_type": "distribution",
                        "supplier_org_id": dist.supplier_org_id,
                        "requirement_id": dist.requirement_id,
                        "hours_overdue": round(hours_since - DEFAULT_SLAS["supplier_response"], 1),
                    })

        # 2. MSP review SLA — submissions waiting for review
        pending_stmt = select(SupplierCandidateSubmission).where(
            SupplierCandidateSubmission.status == VMSSubmissionStatus.SUBMITTED,
        )
        pending_result = await self.session.execute(pending_stmt)
        pending_subs = list(pending_result.scalars().all())

        for sub in pending_subs:
            hours_since = (now - sub.submitted_at.replace(tzinfo=None)).total_seconds() / 3600
            if hours_since > DEFAULT_SLAS["msp_review"]:
                breaches.append({
                    "type": "msp_review",
                    "entity_id": sub.id,
                    "entity_type": "submission",
                    "supplier_org_id": sub.organization_id,
                    "hours_overdue": round(hours_since - DEFAULT_SLAS["msp_review"], 1),
                })

        return breaches

    async def create_placement(
        self,
        msp_org_id: int,
        submission_id: int,
        start_date: Any,
        bill_rate: float,
        pay_rate: float,
        end_date: Optional[Any] = None,
        msp_margin: Optional[float] = None,
        work_location: Optional[str] = None,
        job_title: Optional[str] = None,
        department: Optional[str] = None,
        manager_name: Optional[str] = None,
        manager_email: Optional[str] = None,
    ) -> PlacementRecord:
        """Create a placement record from a successful submission."""
        # Get submission and related data
        sub_stmt = select(SupplierCandidateSubmission).where(
            SupplierCandidateSubmission.id == submission_id
        )
        sub_result = await self.session.execute(sub_stmt)
        submission = sub_result.scalar_one_or_none()

        if not submission:
            raise ValueError(f"Submission {submission_id} not found")

        # Get distribution for requirement and client info
        dist_stmt = select(RequirementDistribution).where(
            RequirementDistribution.id == submission.requirement_distribution_id
        )
        dist_result = await self.session.execute(dist_stmt)
        distribution = dist_result.scalar_one_or_none()

        # Get requirement's client org
        req_stmt = select(Requirement).where(
            Requirement.id == distribution.requirement_id
        )
        req_result = await self.session.execute(req_stmt)
        requirement = req_result.scalar_one_or_none()

        # Determine client org (from requirement's customer or from distribution)
        client_org_id = getattr(requirement, 'customer_id', msp_org_id)

        placement = PlacementRecord(
            organization_id=msp_org_id,
            requirement_id=distribution.requirement_id,
            candidate_id=submission.candidate_id,
            supplier_org_id=submission.organization_id,
            client_org_id=client_org_id,
            supplier_submission_id=submission_id,
            start_date=start_date,
            end_date=end_date,
            bill_rate=bill_rate,
            pay_rate=pay_rate,
            msp_margin=msp_margin or (bill_rate - pay_rate),
            status=PlacementStatus.ACTIVE,
            work_location=work_location,
            job_title=job_title,
            department=department,
            manager_name=manager_name,
            manager_email=manager_email,
        )
        self.session.add(placement)

        # Update submission status to PLACED
        submission.status = VMSSubmissionStatus.PLACED

        # Update distribution status to FILLED
        distribution.status = DistributionStatus.FILLED

        await self.session.commit()
        await self.session.refresh(placement)

        logger.info(f"Created placement for submission {submission_id}")
        return placement

    async def get_active_placements(
        self, org_id: int, org_type: str = "msp",
        offset: int = 0, limit: int = 50,
    ) -> Dict[str, Any]:
        """Get active placements filtered by org type."""
        stmt = select(PlacementRecord).where(
            PlacementRecord.status == PlacementStatus.ACTIVE,
        )

        if org_type == "msp":
            stmt = stmt.where(PlacementRecord.organization_id == org_id)
        elif org_type == "client":
            stmt = stmt.where(PlacementRecord.client_org_id == org_id)
        elif org_type == "supplier":
            stmt = stmt.where(PlacementRecord.supplier_org_id == org_id)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        stmt = stmt.order_by(PlacementRecord.start_date.desc())
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        placements = list(result.scalars().all())

        return {
            "items": placements,
            "total": total,
            "offset": offset,
            "limit": limit,
        }
