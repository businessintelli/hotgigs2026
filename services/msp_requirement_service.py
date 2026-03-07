"""MSP Requirement Service — distribute requirements to suppliers, manage lifecycle."""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from models.organization import Organization
from models.requirement import Requirement
from models.msp_workflow import RequirementDistribution, SupplierCandidateSubmission
from models.enums import DistributionStatus, RequirementStatus

logger = logging.getLogger(__name__)


class MSPRequirementService:
    """Manages requirement distribution from MSP to suppliers."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def distribute_requirement(
        self,
        msp_org_id: int,
        requirement_id: int,
        supplier_org_ids: List[int],
        distributed_by_user_id: int,
        expires_at: Optional[datetime] = None,
        max_submissions: int = 3,
        notes_to_supplier: Optional[str] = None,
    ) -> List[RequirementDistribution]:
        """
        Distribute a requirement to one or more suppliers.
        Creates a RequirementDistribution record per supplier.
        """
        distributions = []

        for supplier_org_id in supplier_org_ids:
            # Check if already distributed to this supplier
            stmt = select(RequirementDistribution).where(
                RequirementDistribution.requirement_id == requirement_id,
                RequirementDistribution.supplier_org_id == supplier_org_id,
                RequirementDistribution.status == DistributionStatus.ACTIVE,
            )
            result = await self.session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                logger.warning(
                    f"Requirement {requirement_id} already distributed to supplier {supplier_org_id}"
                )
                distributions.append(existing)
                continue

            dist = RequirementDistribution(
                organization_id=msp_org_id,
                requirement_id=requirement_id,
                supplier_org_id=supplier_org_id,
                distributed_by_user_id=distributed_by_user_id,
                distributed_at=datetime.utcnow(),
                expires_at=expires_at,
                status=DistributionStatus.ACTIVE,
                max_submissions=max_submissions,
                notes_to_supplier=notes_to_supplier,
            )
            self.session.add(dist)
            distributions.append(dist)

        await self.session.flush()
        await self.session.commit()

        logger.info(
            f"Distributed requirement {requirement_id} to {len(supplier_org_ids)} suppliers"
        )
        return distributions

    async def revoke_distribution(self, distribution_id: int) -> RequirementDistribution:
        """Revoke a supplier's access to a requirement."""
        stmt = select(RequirementDistribution).where(
            RequirementDistribution.id == distribution_id
        )
        result = await self.session.execute(stmt)
        dist = result.scalar_one_or_none()

        if not dist:
            raise ValueError(f"Distribution {distribution_id} not found")

        dist.status = DistributionStatus.REVOKED
        await self.session.commit()
        return dist

    async def get_distributions_for_requirement(
        self, requirement_id: int, include_expired: bool = False
    ) -> List[Dict[str, Any]]:
        """Get all distributions for a requirement with submission counts."""
        stmt = select(RequirementDistribution).where(
            RequirementDistribution.requirement_id == requirement_id,
        )
        if not include_expired:
            stmt = stmt.where(
                RequirementDistribution.status.in_([
                    DistributionStatus.ACTIVE,
                    DistributionStatus.FILLED,
                ])
            )
        stmt = stmt.order_by(RequirementDistribution.distributed_at.desc())

        result = await self.session.execute(stmt)
        distributions = list(result.scalars().all())

        # Get submission counts per distribution
        enriched = []
        for dist in distributions:
            count_stmt = select(func.count(SupplierCandidateSubmission.id)).where(
                SupplierCandidateSubmission.requirement_distribution_id == dist.id
            )
            count_result = await self.session.execute(count_stmt)
            sub_count = count_result.scalar() or 0

            # Get supplier org name
            org_stmt = select(Organization.name).where(Organization.id == dist.supplier_org_id)
            org_result = await self.session.execute(org_stmt)
            supplier_name = org_result.scalar() or "Unknown"

            enriched.append({
                "distribution": dist,
                "submission_count": sub_count,
                "supplier_org_name": supplier_name,
            })

        return enriched

    async def get_supplier_opportunities(
        self, supplier_org_id: int, status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get requirements distributed to a supplier (supplier's view)."""
        stmt = select(RequirementDistribution).where(
            RequirementDistribution.supplier_org_id == supplier_org_id,
        )
        if status_filter:
            stmt = stmt.where(RequirementDistribution.status == status_filter)
        else:
            stmt = stmt.where(RequirementDistribution.status == DistributionStatus.ACTIVE)

        stmt = stmt.order_by(RequirementDistribution.distributed_at.desc())
        result = await self.session.execute(stmt)
        distributions = list(result.scalars().all())

        enriched = []
        for dist in distributions:
            # Get requirement details
            req_stmt = select(Requirement).where(Requirement.id == dist.requirement_id)
            req_result = await self.session.execute(req_stmt)
            requirement = req_result.scalar_one_or_none()

            # Count my submissions
            count_stmt = select(func.count(SupplierCandidateSubmission.id)).where(
                SupplierCandidateSubmission.requirement_distribution_id == dist.id,
                SupplierCandidateSubmission.organization_id == supplier_org_id,
            )
            count_result = await self.session.execute(count_stmt)
            my_submissions = count_result.scalar() or 0

            enriched.append({
                "distribution": dist,
                "requirement": requirement,
                "my_submission_count": my_submissions,
                "remaining_submissions": dist.max_submissions - my_submissions,
            })

        return enriched

    async def check_expired_distributions(self) -> int:
        """Mark expired distributions. Called by scheduler."""
        stmt = select(RequirementDistribution).where(
            RequirementDistribution.status == DistributionStatus.ACTIVE,
            RequirementDistribution.expires_at != None,
            RequirementDistribution.expires_at < datetime.utcnow(),
        )
        result = await self.session.execute(stmt)
        expired = list(result.scalars().all())

        for dist in expired:
            dist.status = DistributionStatus.EXPIRED

        if expired:
            await self.session.commit()
            logger.info(f"Expired {len(expired)} distributions")

        return len(expired)
