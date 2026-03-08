"""Automated invoice generation endpoints for VMS."""

import logging
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.dependencies import get_current_user, get_db, require_role, get_tenant_context_dep
from database.tenant_context import TenantContext
from models.user import User
from models.invoice import Invoice
from schemas.invoice import InvoiceResponse, InvoiceDetailResponse
from services.auto_invoice_service import AutoInvoiceService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/invoicing", tags=["Auto Invoicing"])


@router.post("/generate", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def generate_invoices(
    client_org_id: int = Query(...),
    period_start: date = Query(...),
    period_end: date = Query(...),
    user: User = Depends(require_role("msp_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """Generate invoices from approved timesheets for a period."""
    try:
        svc = AutoInvoiceService(db)
        invoice = await svc.generate_invoice_from_timesheets(
            client_org_id=client_org_id,
            period_start=period_start,
            period_end=period_end,
        )

        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No approved timesheets found for invoice generation"
            )

        return InvoiceResponse.model_validate(invoice)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating invoice: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/preview", response_model=dict)
async def preview_invoice_generation(
    client_org_id: int = Query(...),
    period_start: date = Query(...),
    period_end: date = Query(...),
    user: User = Depends(require_role("msp_admin", "client_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """Preview what invoices would be generated without creating them."""
    try:
        svc = AutoInvoiceService(db)
        preview = await svc.preview_invoice(
            client_org_id=client_org_id,
            period_start=period_start,
            period_end=period_end,
        )
        return preview
    except Exception as e:
        logger.error(f"Error previewing invoice: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/supplier-remittance", response_model=dict, status_code=status.HTTP_201_CREATED)
async def generate_supplier_remittance(
    supplier_org_id: int = Query(...),
    period_start: date = Query(...),
    period_end: date = Query(...),
    user: User = Depends(require_role("msp_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """Generate a supplier payment statement/remittance for a period."""
    try:
        # Query approved timesheets for supplier
        from models.timesheet import Timesheet
        from models.msp_workflow import PlacementRecord

        result = await db.execute(
            select(Timesheet).join(
                PlacementRecord, Timesheet.placement_id == PlacementRecord.id
            ).where(
                PlacementRecord.supplier_org_id == supplier_org_id,
                Timesheet.status == "APPROVED",
                Timesheet.period_start >= period_start,
                Timesheet.period_end <= period_end,
            )
        )
        timesheets = result.scalars().all()

        if not timesheets:
            return {
                "supplier_org_id": supplier_org_id,
                "period_start": str(period_start),
                "period_end": str(period_end),
                "total_timesheets": 0,
                "total_hours": 0.0,
                "total_amount": 0.0,
                "status": "no_timesheets"
            }

        total_hours = sum(ts.total_hours or 0 for ts in timesheets)
        total_amount = sum(ts.total_pay_amount or 0 for ts in timesheets)

        return {
            "supplier_org_id": supplier_org_id,
            "period_start": str(period_start),
            "period_end": str(period_end),
            "total_timesheets": len(timesheets),
            "total_hours": total_hours,
            "total_amount": total_amount,
            "status": "generated"
        }
    except Exception as e:
        logger.error(f"Error generating supplier remittance: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
