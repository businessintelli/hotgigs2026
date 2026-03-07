"""MSP Analytics Service — dashboard metrics, supplier scorecards, client metrics."""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, and_

from models.organization import Organization
from models.requirement import Requirement
from models.msp_workflow import (
    RequirementDistribution, SupplierCandidateSubmission,
    MSPReview, ClientFeedback, PlacementRecord,
)
from models.enums import (
    OrganizationType, DistributionStatus, VMSSubmissionStatus,
    PlacementStatus, RequirementStatus, OrgOnboardingStatus,
)

logger = logging.getLogger(__name__)


class MSPAnalyticsService:
    """Provides analytics and metrics for the MSP dashboard."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_msp_dashboard_metrics(self, msp_org_id: int) -> Dict[str, Any]:
        """Aggregate KPIs for the MSP dashboard."""
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Total clients
        client_count = await self.session.execute(
            select(func.count(Organization.id)).where(
                Organization.parent_org_id == msp_org_id,
                Organization.org_type == OrganizationType.CLIENT,
                Organization.is_active == True,
            )
        )
        total_clients = client_count.scalar() or 0

        # Total suppliers
        supplier_count = await self.session.execute(
            select(func.count(Organization.id)).where(
                Organization.parent_org_id == msp_org_id,
                Organization.org_type == OrganizationType.SUPPLIER,
                Organization.is_active == True,
            )
        )
        total_suppliers = supplier_count.scalar() or 0

        # Active distributions
        active_dist = await self.session.execute(
            select(func.count(RequirementDistribution.id)).where(
                RequirementDistribution.organization_id == msp_org_id,
                RequirementDistribution.status == DistributionStatus.ACTIVE,
            )
        )
        total_distributions = active_dist.scalar() or 0

        # Pending submissions (need MSP review)
        pending_subs = await self.session.execute(
            select(func.count(SupplierCandidateSubmission.id)).where(
                SupplierCandidateSubmission.status == VMSSubmissionStatus.SUBMITTED,
            )
        )
        pending_submissions = pending_subs.scalar() or 0

        # Submissions this month
        monthly_subs = await self.session.execute(
            select(func.count(SupplierCandidateSubmission.id)).where(
                SupplierCandidateSubmission.submitted_at >= month_start,
            )
        )
        submissions_this_month = monthly_subs.scalar() or 0

        # Active placements
        active_place = await self.session.execute(
            select(func.count(PlacementRecord.id)).where(
                PlacementRecord.organization_id == msp_org_id,
                PlacementRecord.status == PlacementStatus.ACTIVE,
            )
        )
        active_placements = active_place.scalar() or 0

        # Placements this month
        monthly_place = await self.session.execute(
            select(func.count(PlacementRecord.id)).where(
                PlacementRecord.organization_id == msp_org_id,
                PlacementRecord.created_at >= month_start,
            )
        )
        placements_this_month = monthly_place.scalar() or 0

        # Avg quality score
        avg_quality = await self.session.execute(
            select(func.avg(SupplierCandidateSubmission.quality_score)).where(
                SupplierCandidateSubmission.quality_score != None,
            )
        )
        avg_submission_quality = avg_quality.scalar()

        return {
            "total_clients": total_clients,
            "total_suppliers": total_suppliers,
            "active_requirements": total_distributions,
            "total_distributions": total_distributions,
            "pending_submissions": pending_submissions,
            "submissions_this_month": submissions_this_month,
            "active_placements": active_placements,
            "placements_this_month": placements_this_month,
            "avg_submission_quality": round(avg_submission_quality, 2) if avg_submission_quality else None,
        }

    async def get_supplier_scorecard(self, supplier_org_id: int) -> Dict[str, Any]:
        """Calculate supplier performance scorecard."""
        # Get org info
        org_stmt = select(Organization).where(Organization.id == supplier_org_id)
        org_result = await self.session.execute(org_stmt)
        org = org_result.scalar_one_or_none()

        if not org:
            raise ValueError(f"Supplier org {supplier_org_id} not found")

        # Total submissions
        total_subs = await self.session.execute(
            select(func.count(SupplierCandidateSubmission.id)).where(
                SupplierCandidateSubmission.organization_id == supplier_org_id,
            )
        )
        total_submissions = total_subs.scalar() or 0

        # Approved submissions
        approved = await self.session.execute(
            select(func.count(SupplierCandidateSubmission.id)).where(
                SupplierCandidateSubmission.organization_id == supplier_org_id,
                SupplierCandidateSubmission.status.in_([
                    VMSSubmissionStatus.MSP_APPROVED,
                    VMSSubmissionStatus.SUBMITTED_TO_CLIENT,
                    VMSSubmissionStatus.CLIENT_SHORTLISTED,
                    VMSSubmissionStatus.INTERVIEW,
                    VMSSubmissionStatus.OFFER,
                    VMSSubmissionStatus.PLACED,
                ]),
            )
        )
        approved_submissions = approved.scalar() or 0

        # Rejected
        rejected = await self.session.execute(
            select(func.count(SupplierCandidateSubmission.id)).where(
                SupplierCandidateSubmission.organization_id == supplier_org_id,
                SupplierCandidateSubmission.status.in_([
                    VMSSubmissionStatus.MSP_REJECTED,
                    VMSSubmissionStatus.CLIENT_REJECTED,
                ]),
            )
        )
        rejected_submissions = rejected.scalar() or 0

        # Placements
        placements = await self.session.execute(
            select(func.count(PlacementRecord.id)).where(
                PlacementRecord.supplier_org_id == supplier_org_id,
            )
        )
        total_placements = placements.scalar() or 0

        # Avg quality score
        avg_qual = await self.session.execute(
            select(func.avg(SupplierCandidateSubmission.quality_score)).where(
                SupplierCandidateSubmission.organization_id == supplier_org_id,
                SupplierCandidateSubmission.quality_score != None,
            )
        )
        avg_quality = avg_qual.scalar()

        return {
            "supplier_org_id": supplier_org_id,
            "supplier_name": org.name,
            "tier": str(org.tier) if org.tier else None,
            "total_submissions": total_submissions,
            "approved_submissions": approved_submissions,
            "rejected_submissions": rejected_submissions,
            "total_placements": total_placements,
            "avg_quality_score": round(avg_quality, 2) if avg_quality else None,
            "approval_rate": round(approved_submissions / total_submissions * 100, 1) if total_submissions > 0 else 0,
        }

    async def get_client_metrics(self, client_org_id: int) -> Dict[str, Any]:
        """Calculate client-specific metrics."""
        org_stmt = select(Organization).where(Organization.id == client_org_id)
        org_result = await self.session.execute(org_stmt)
        org = org_result.scalar_one_or_none()

        if not org:
            raise ValueError(f"Client org {client_org_id} not found")

        # Active placements for this client
        active = await self.session.execute(
            select(func.count(PlacementRecord.id)).where(
                PlacementRecord.client_org_id == client_org_id,
                PlacementRecord.status == PlacementStatus.ACTIVE,
            )
        )
        active_placements = active.scalar() or 0

        # Total placements
        total = await self.session.execute(
            select(func.count(PlacementRecord.id)).where(
                PlacementRecord.client_org_id == client_org_id,
            )
        )
        total_placements = total.scalar() or 0

        return {
            "client_org_id": client_org_id,
            "client_name": org.name,
            "active_placements": active_placements,
            "total_placements": total_placements,
        }
