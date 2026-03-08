"""Automated invoice generation from approved timesheets."""
import logging
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from models.timesheet import Timesheet
from models.invoice import Invoice, InvoiceLineItem
from models.msp_workflow import PlacementRecord

logger = logging.getLogger(__name__)


class AutoInvoiceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_invoice_from_timesheets(
        self, client_org_id: int, period_start: date, period_end: date,
    ) -> Optional[Invoice]:
        # Get approved timesheets for client's placements in period
        result = await self.db.execute(
            select(Timesheet).join(
                PlacementRecord, Timesheet.placement_id == PlacementRecord.id
            ).where(and_(
                PlacementRecord.client_org_id == client_org_id,
                Timesheet.status == "APPROVED",
                Timesheet.period_start >= period_start,
                Timesheet.period_end <= period_end,
                Timesheet.invoice_id.is_(None),
            ))
        )
        timesheets = list(result.scalars().all())

        if not timesheets:
            return None

        subtotal = sum(ts.total_bill_amount or 0 for ts in timesheets)
        inv_number = f"INV-{client_org_id}-{period_start.strftime('%Y%m%d')}"

        invoice = Invoice(
            customer_id=client_org_id,
            invoice_number=inv_number,
            invoice_date=datetime.utcnow().date(),
            due_date=date(period_end.year, period_end.month + 1 if period_end.month < 12 else 1,
                         min(period_end.day, 28)),
            period_start=period_start,
            period_end=period_end,
            subtotal=subtotal,
            tax_amount=0,
            total_amount=subtotal,
            amount_due=subtotal,
            status="DRAFT",
            payment_terms="net_30",
        )
        self.db.add(invoice)
        await self.db.flush()

        for ts in timesheets:
            line = InvoiceLineItem(
                invoice_id=invoice.id,
                timesheet_id=ts.id,
                description=f"Services for period {ts.period_start} to {ts.period_end}",
                quantity=ts.total_hours or 0,
                unit_type="hours",
                unit_price=ts.bill_rate or 0,
                amount=ts.total_bill_amount or 0,
            )
            self.db.add(line)
            ts.invoice_id = invoice.id

        await self.db.commit()
        await self.db.refresh(invoice)
        logger.info(f"Generated invoice {invoice.invoice_number} for ${subtotal:.2f}")
        return invoice

    async def preview_invoice(
        self, client_org_id: int, period_start: date, period_end: date,
    ) -> Dict[str, Any]:
        result = await self.db.execute(
            select(Timesheet).join(
                PlacementRecord, Timesheet.placement_id == PlacementRecord.id
            ).where(and_(
                PlacementRecord.client_org_id == client_org_id,
                Timesheet.status == "APPROVED",
                Timesheet.period_start >= period_start,
                Timesheet.period_end <= period_end,
                Timesheet.invoice_id.is_(None),
            ))
        )
        timesheets = list(result.scalars().all())

        return {
            "client_org_id": client_org_id,
            "period_start": str(period_start),
            "period_end": str(period_end),
            "timesheet_count": len(timesheets),
            "total_hours": sum(ts.total_hours or 0 for ts in timesheets),
            "total_amount": sum(ts.total_bill_amount or 0 for ts in timesheets),
        }
