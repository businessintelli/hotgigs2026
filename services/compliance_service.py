"""Compliance tracking service."""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from models.compliance import ComplianceRequirement, ComplianceRecord, ComplianceScore
from models.msp_workflow import PlacementRecord

logger = logging.getLogger(__name__)


class ComplianceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_requirement(self, data: dict) -> ComplianceRequirement:
        req = ComplianceRequirement(**data)
        self.db.add(req)
        await self.db.commit()
        await self.db.refresh(req)
        return req

    async def create_record(self, data: dict) -> ComplianceRecord:
        record = ComplianceRecord(**data)
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def update_record_status(
        self, record_id: int, status: str,
        verified_by: Optional[int] = None, notes: Optional[str] = None,
    ) -> ComplianceRecord:
        result = await self.db.execute(
            select(ComplianceRecord).where(ComplianceRecord.id == record_id)
        )
        record = result.scalar_one_or_none()
        if not record:
            raise ValueError(f"Compliance record {record_id} not found")

        record.status = status
        if verified_by:
            record.verified_by = verified_by
            record.verification_date = datetime.utcnow().date()
        if notes:
            record.verification_notes = notes
        if status == "COMPLETED":
            record.completed_at = datetime.utcnow()
            record.passed = True
        elif status == "FAILED":
            record.passed = False

        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def check_placement_compliance(self, placement_id: int) -> Tuple[bool, Dict[str, Any]]:
        result = await self.db.execute(
            select(ComplianceRecord).where(ComplianceRecord.placement_id == placement_id)
        )
        records = list(result.scalars().all())
        if not records:
            return True, {"total": 0, "completed": 0, "expired": 0, "failed": 0, "gaps": []}

        completed = expired = failed = 0
        gaps = []
        for r in records:
            s = r.status if isinstance(r.status, str) else r.status.value if hasattr(r.status, 'value') else str(r.status)
            if s.upper() == "COMPLETED":
                completed += 1
                if r.expires_at and r.expires_at < datetime.utcnow():
                    expired += 1
            elif s.upper() == "FAILED":
                failed += 1
                gaps.append(r.id)
            else:
                gaps.append(r.id)

        is_compliant = len(gaps) == 0 and expired == 0
        return is_compliant, {"total": len(records), "completed": completed,
                             "expired": expired, "failed": failed, "gaps": gaps}

    async def get_expiring_compliance(self, days_ahead: int = 30) -> List[ComplianceRecord]:
        cutoff = datetime.utcnow() + timedelta(days=days_ahead)
        result = await self.db.execute(
            select(ComplianceRecord).where(and_(
                ComplianceRecord.expires_at.isnot(None),
                ComplianceRecord.expires_at <= cutoff,
                ComplianceRecord.expires_at > datetime.utcnow(),
            ))
        )
        return list(result.scalars().all())

    async def calculate_supplier_compliance_score(self, supplier_org_id: int) -> Dict[str, Any]:
        result = await self.db.execute(
            select(PlacementRecord).where(
                PlacementRecord.supplier_org_id == supplier_org_id,
                PlacementRecord.is_active == True,
            )
        )
        placements = list(result.scalars().all())

        total = completed = expired = failed = 0
        for p in placements:
            res = await self.db.execute(
                select(ComplianceRecord).where(ComplianceRecord.placement_id == p.id)
            )
            records = list(res.scalars().all())
            total += len(records)
            for r in records:
                s = r.status if isinstance(r.status, str) else str(r.status)
                if "COMPLETED" in s.upper():
                    completed += 1
                    if r.expires_at and r.expires_at < datetime.utcnow():
                        expired += 1
                elif "FAILED" in s.upper():
                    failed += 1

        score = ((completed - expired - failed) / total * 100) if total > 0 else 100.0
        score = max(0.0, min(100.0, score))

        # Upsert
        existing = await self.db.execute(
            select(ComplianceScore).where(ComplianceScore.supplier_org_id == supplier_org_id)
        )
        cs = existing.scalar_one_or_none()
        if cs:
            cs.overall_score = score
            cs.completed_requirements = completed
            cs.total_requirements = total
            cs.expired_requirements = expired
            cs.failed_requirements = failed
            cs.last_calculated_at = datetime.utcnow()
        else:
            cs = ComplianceScore(
                supplier_org_id=supplier_org_id, overall_score=score,
                completed_requirements=completed, total_requirements=total,
                expired_requirements=expired, failed_requirements=failed,
                last_calculated_at=datetime.utcnow(),
            )
            self.db.add(cs)

        await self.db.commit()
        return {"supplier_org_id": supplier_org_id, "overall_score": score,
                "completed": completed, "total": total, "expired": expired, "failed": failed}
