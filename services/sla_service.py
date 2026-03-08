"""SLA configuration and breach detection service."""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from models.sla import SLAConfiguration, SLABreachRecord

logger = logging.getLogger(__name__)


class SLAService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_config(self, data: dict) -> SLAConfiguration:
        config = SLAConfiguration(**data)
        self.db.add(config)
        await self.db.commit()
        await self.db.refresh(config)
        return config

    async def list_configs(self, organization_id: Optional[int] = None) -> List[SLAConfiguration]:
        query = select(SLAConfiguration).where(SLAConfiguration.is_active == True)
        if organization_id:
            query = query.where(SLAConfiguration.organization_id == organization_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def record_breach(
        self, sla_config_id: int, metric_type: str, severity: str,
        threshold: float, actual: float, requirement_id: Optional[int] = None,
        supplier_org_id: Optional[int] = None, penalty: Optional[float] = None,
    ) -> SLABreachRecord:
        breach = SLABreachRecord(
            sla_config_id=sla_config_id, requirement_id=requirement_id,
            supplier_org_id=supplier_org_id, metric_type=metric_type,
            severity=severity, threshold_value=threshold,
            actual_value=actual, variance=actual - threshold,
            penalty_amount=penalty, detected_at=datetime.utcnow(),
        )
        self.db.add(breach)
        await self.db.commit()
        await self.db.refresh(breach)
        return breach

    async def resolve_breach(self, breach_id: int, resolved_by: int, notes: str) -> SLABreachRecord:
        result = await self.db.execute(
            select(SLABreachRecord).where(SLABreachRecord.id == breach_id)
        )
        breach = result.scalar_one_or_none()
        if not breach:
            raise ValueError(f"Breach {breach_id} not found")

        breach.resolved_at = datetime.utcnow()
        breach.resolved_by = resolved_by
        breach.resolution_notes = notes
        await self.db.commit()
        await self.db.refresh(breach)
        return breach

    async def list_breaches(
        self, organization_id: Optional[int] = None,
        severity: Optional[str] = None, resolved: Optional[bool] = None,
    ) -> List[SLABreachRecord]:
        query = select(SLABreachRecord).join(SLAConfiguration)
        if organization_id:
            query = query.where(SLAConfiguration.organization_id == organization_id)
        if severity:
            query = query.where(SLABreachRecord.severity == severity)
        if resolved is True:
            query = query.where(SLABreachRecord.resolved_at.isnot(None))
        elif resolved is False:
            query = query.where(SLABreachRecord.resolved_at.is_(None))
        result = await self.db.execute(query.order_by(SLABreachRecord.detected_at.desc()))
        return list(result.scalars().all())

    async def get_sla_dashboard(self, organization_id: int) -> Dict[str, Any]:
        configs = await self.list_configs(organization_id)
        all_breaches = await self.list_breaches(organization_id)

        active = [b for b in all_breaches if not b.resolved_at]
        resolved = [b for b in all_breaches if b.resolved_at]

        by_metric = {}
        by_severity = {}
        total_penalties = 0.0
        critical_count = 0

        for b in all_breaches:
            m = b.metric_type if isinstance(b.metric_type, str) else str(b.metric_type)
            s = b.severity if isinstance(b.severity, str) else str(b.severity)
            by_metric[m] = by_metric.get(m, 0) + 1
            by_severity[s] = by_severity.get(s, 0) + 1
            if b.penalty_amount:
                total_penalties += b.penalty_amount
            if "CRITICAL" in s.upper():
                critical_count += 1

        return {
            "total_configs": len(configs),
            "active_breaches": len(active),
            "resolved_breaches": len(resolved),
            "critical_breaches": critical_count,
            "total_penalties": total_penalties,
            "breaches_by_metric": by_metric,
            "breaches_by_severity": by_severity,
        }
