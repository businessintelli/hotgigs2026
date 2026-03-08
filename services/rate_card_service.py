"""Rate card management service."""
import logging
from typing import List, Tuple, Optional, Dict, Any
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from models.rate_card import RateCard, RateCardEntry
from models.organization import Organization

logger = logging.getLogger(__name__)


class RateCardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_rate_card(self, data: dict) -> RateCard:
        result = await self.db.execute(
            select(Organization).where(Organization.id == data["client_org_id"])
        )
        if not result.scalar_one_or_none():
            raise ValueError(f"Client organization {data['client_org_id']} not found")

        entries_data = data.pop("entries", [])
        rate_card = RateCard(**data)
        for entry in entries_data:
            rate_card.entries.append(RateCardEntry(**entry))

        self.db.add(rate_card)
        await self.db.commit()
        await self.db.refresh(rate_card)
        return rate_card

    async def get_applicable_rate_card(
        self, client_org_id: int, job_category: str,
        location: Optional[str] = None, effective_date: Optional[date] = None,
    ) -> Optional[RateCard]:
        if not effective_date:
            effective_date = date.today()

        query = select(RateCard).where(and_(
            RateCard.client_org_id == client_org_id,
            RateCard.job_category == job_category,
            RateCard.is_active == True,
            RateCard.effective_from <= effective_date,
            or_(RateCard.effective_to.is_(None), RateCard.effective_to >= effective_date),
        ))

        if location:
            query = query.where(or_(RateCard.location == location, RateCard.location.is_(None)))

        result = await self.db.execute(query.order_by(desc(RateCard.created_at)))
        return result.scalars().first()

    async def validate_submission_rates(
        self, client_org_id: int, job_category: str,
        bill_rate: float, pay_rate: float, location: Optional[str] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        rate_card = await self.get_applicable_rate_card(client_org_id, job_category, location)
        if not rate_card:
            return True, {"status": "no_rate_card", "message": "No rate card found", "violations": []}

        violations = []
        if bill_rate < rate_card.bill_rate_min or bill_rate > rate_card.bill_rate_max:
            violations.append({"field": "bill_rate", "actual": bill_rate,
                             "min": rate_card.bill_rate_min, "max": rate_card.bill_rate_max})
        if pay_rate < rate_card.pay_rate_min or pay_rate > rate_card.pay_rate_max:
            violations.append({"field": "pay_rate", "actual": pay_rate,
                             "min": rate_card.pay_rate_min, "max": rate_card.pay_rate_max})

        return len(violations) == 0, {"violations": violations, "rate_card_id": rate_card.id}

    async def list_rate_cards(self, client_org_id: Optional[int] = None, status: Optional[str] = None) -> List[RateCard]:
        query = select(RateCard).where(RateCard.is_active == True)
        if client_org_id:
            query = query.where(RateCard.client_org_id == client_org_id)
        if status:
            query = query.where(RateCard.status == status)
        result = await self.db.execute(query.order_by(desc(RateCard.created_at)))
        return list(result.scalars().all())
