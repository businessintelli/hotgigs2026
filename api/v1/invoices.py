"""Invoicing API endpoints."""

import logging
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from schemas.invoice import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    InvoiceDetailResponse,
    InvoiceLineItemCreate,
    InvoiceLineItemUpdate,
    InvoiceLineItemResponse,
    InvoicePaymentCreate,
    InvoicePaymentResponse,
    CreditMemoCreate,
    CreditMemoResponse,
    InvoiceListFilter,
    SendInvoiceRequest,
    InvoiceAnalyticsResponse,
    InvoiceAgingResponse,
    RevenueReport,
    GenerateInvoiceFromTimesheetRequest,
    BulkGenerateInvoicesRequest,
    QuickBooksConnectRequest,
    QuickBooksConnectResponse,
    QuickBooksSyncRequest,
    QuickBooksSyncResponse,
    QuickBooksStatusResponse,
    QuickBooksAccountMapping,
)
from schemas.common import PaginatedResponse
from services.invoicing_service import InvoicingService, QuickBooksIntegrationService
from agents.invoicing_agent import InvoicingAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/invoices", tags=["invoices"])
invoicing_agent = InvoicingAgent()


# ===== INVOICE ENDPOINTS =====


@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice_data: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
) -> InvoiceResponse:
    """Create a new invoice.

    Args:
        invoice_data: Invoice creation data
        db: Database session

    Returns:
        Created invoice
    """
    try:
        invoice = await invoicing_agent.create_invoice(db, invoice_data.model_dump())
        return InvoiceResponse.from_orm(invoice)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating invoice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create invoice",
        )


@router.get("", response_model=PaginatedResponse[InvoiceResponse])
async def list_invoices(
    customer_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    invoice_date_start: Optional[date] = Query(None),
    invoice_date_end: Optional[date] = Query(None),
    due_date_start: Optional[date] = Query(None),
    due_date_end: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[InvoiceResponse]:
    """List invoices with filters.

    Args:
        customer_id: Filter by customer
        status: Filter by status
        invoice_date_start: Filter by invoice date start
        invoice_date_end: Filter by invoice date end
        due_date_start: Filter by due date start
        due_date_end: Filter by due date end
        skip: Skip records
        limit: Limit records
        db: Database session

    Returns:
        Paginated invoices
    """
    try:
        filters = InvoiceListFilter(
            customer_id=customer_id,
            status=status,
            invoice_date_start=invoice_date_start,
            invoice_date_end=invoice_date_end,
            due_date_start=due_date_start,
            due_date_end=due_date_end,
            skip=skip,
            limit=limit,
        )

        service = InvoicingService(db)
        invoices, total = await service.get_invoices(filters)

        items = [InvoiceResponse.from_orm(inv) for inv in invoices]

        return PaginatedResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
        )

    except Exception as e:
        logger.error(f"Error listing invoices: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list invoices",
        )


@router.get("/{invoice_id}", response_model=InvoiceDetailResponse)
async def get_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
) -> InvoiceDetailResponse:
    """Get invoice details.

    Args:
        invoice_id: Invoice ID
        db: Database session

    Returns:
        Invoice with line items and payments
    """
    try:
        service = InvoicingService(db)
        invoice = await service.get_invoice(invoice_id)

        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found",
            )

        return InvoiceDetailResponse.from_orm(invoice)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting invoice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get invoice",
        )


@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: int,
    update_data: InvoiceUpdate,
    db: AsyncSession = Depends(get_db),
) -> InvoiceResponse:
    """Update invoice.

    Args:
        invoice_id: Invoice ID
        update_data: Update data
        db: Database session

    Returns:
        Updated invoice
    """
    try:
        service = InvoicingService(db)
        invoice = await service.update_invoice(invoice_id, update_data)
        return InvoiceResponse.from_orm(invoice)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating invoice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update invoice",
        )


# ===== LINE ITEM ENDPOINTS =====


@router.post(
    "/{invoice_id}/line-items",
    response_model=InvoiceLineItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_line_item(
    invoice_id: int,
    item_data: InvoiceLineItemCreate,
    db: AsyncSession = Depends(get_db),
) -> InvoiceLineItemResponse:
    """Add line item to invoice.

    Args:
        invoice_id: Invoice ID
        item_data: Line item data
        db: Database session

    Returns:
        Created line item
    """
    try:
        service = InvoicingService(db)
        item = await service.add_line_item(invoice_id, item_data)
        return InvoiceLineItemResponse.from_orm(item)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding line item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add line item",
        )


@router.put("/{invoice_id}/line-items/{item_id}", response_model=InvoiceLineItemResponse)
async def update_line_item(
    invoice_id: int,
    item_id: int,
    update_data: InvoiceLineItemUpdate,
    db: AsyncSession = Depends(get_db),
) -> InvoiceLineItemResponse:
    """Update line item.

    Args:
        invoice_id: Invoice ID
        item_id: Line item ID
        update_data: Update data
        db: Database session

    Returns:
        Updated line item
    """
    try:
        service = InvoicingService(db)
        item = await service.update_line_item(item_id, update_data)
        return InvoiceLineItemResponse.from_orm(item)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating line item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update line item",
        )


@router.delete("/{invoice_id}/line-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_line_item(
    invoice_id: int,
    item_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete line item.

    Args:
        invoice_id: Invoice ID
        item_id: Line item ID
        db: Database session
    """
    try:
        service = InvoicingService(db)
        await service.delete_line_item(item_id)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting line item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete line item",
        )


# ===== INVOICE GENERATION ENDPOINTS =====


@router.post("/generate-from-timesheet/{timesheet_id}", response_model=InvoiceResponse)
async def generate_from_timesheet(
    timesheet_id: int,
    apply_markup: bool = Query(True),
    db: AsyncSession = Depends(get_db),
) -> InvoiceResponse:
    """Generate invoice from timesheet.

    Args:
        timesheet_id: Timesheet ID
        apply_markup: Whether to apply markup
        db: Database session

    Returns:
        Created invoice
    """
    try:
        invoice = await invoicing_agent.generate_invoice_from_timesheet(
            db, timesheet_id, apply_markup
        )
        return InvoiceResponse.from_orm(invoice)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating invoice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate invoice",
        )


@router.post("/generate-bulk", response_model=list)
async def bulk_generate_invoices(
    request: BulkGenerateInvoicesRequest,
    db: AsyncSession = Depends(get_db),
) -> list:
    """Bulk generate invoices.

    Args:
        request: Bulk generation request
        db: Database session

    Returns:
        List of created invoices
    """
    try:
        invoices = await invoicing_agent.generate_bulk_invoices(
            db,
            request.period_start,
            request.period_end,
            request.customer_id,
            request.apply_markup,
        )
        return [InvoiceResponse.from_orm(inv).model_dump() for inv in invoices]

    except Exception as e:
        logger.error(f"Error bulk generating invoices: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to bulk generate invoices",
        )


# ===== PAYMENT ENDPOINTS =====


@router.post(
    "/{invoice_id}/record-payment",
    response_model=InvoicePaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def record_payment(
    invoice_id: int,
    payment_data: InvoicePaymentCreate,
    db: AsyncSession = Depends(get_db),
) -> InvoicePaymentResponse:
    """Record payment against invoice.

    Args:
        invoice_id: Invoice ID
        payment_data: Payment data
        db: Database session

    Returns:
        Created payment
    """
    try:
        payment = await invoicing_agent.record_payment(db, invoice_id, payment_data.model_dump())
        return InvoicePaymentResponse.from_orm(payment)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error recording payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record payment",
        )


# ===== INVOICE MANAGEMENT ENDPOINTS =====


@router.post("/{invoice_id}/send", response_model=dict)
async def send_invoice(
    invoice_id: int,
    request: SendInvoiceRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Send invoice to customer.

    Args:
        invoice_id: Invoice ID
        request: Send request
        db: Database session

    Returns:
        Delivery confirmation
    """
    try:
        result = await invoicing_agent.send_invoice(
            db, invoice_id, request.delivery_method, request.recipient_email
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error sending invoice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send invoice",
        )


@router.post("/{invoice_id}/void", response_model=InvoiceResponse)
async def void_invoice(
    invoice_id: int,
    reason: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> InvoiceResponse:
    """Void invoice.

    Args:
        invoice_id: Invoice ID
        reason: Voiding reason
        db: Database session

    Returns:
        Updated invoice
    """
    try:
        invoice = await invoicing_agent.void_invoice(db, invoice_id, reason)
        return InvoiceResponse.from_orm(invoice)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error voiding invoice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to void invoice",
        )


@router.post("/{invoice_id}/credit-memo", response_model=CreditMemoResponse)
async def create_credit_memo(
    invoice_id: int,
    memo_data: CreditMemoCreate,
    db: AsyncSession = Depends(get_db),
) -> CreditMemoResponse:
    """Create credit memo.

    Args:
        invoice_id: Invoice ID
        memo_data: Memo data
        db: Database session

    Returns:
        Created credit memo
    """
    try:
        memo = await invoicing_agent.create_credit_memo(db, invoice_id, memo_data.model_dump())
        return CreditMemoResponse.from_orm(memo)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating credit memo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create credit memo",
        )


# ===== ANALYTICS ENDPOINTS =====


@router.get("/pdf/{invoice_id}")
async def generate_invoice_pdf(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Generate invoice PDF.

    Args:
        invoice_id: Invoice ID
        db: Database session

    Returns:
        PDF file info
    """
    try:
        file_path = await invoicing_agent.generate_invoice_pdf(db, invoice_id)
        return {"file_path": file_path}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate PDF",
        )


@router.get("/aging-report", response_model=InvoiceAgingResponse)
async def get_aging_report(
    db: AsyncSession = Depends(get_db),
) -> InvoiceAgingResponse:
    """Get accounts receivable aging report.

    Args:
        db: Database session

    Returns:
        Aging report
    """
    try:
        report = await invoicing_agent.get_aging_report(db)
        return InvoiceAgingResponse(**report)

    except Exception as e:
        logger.error(f"Error getting aging report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get aging report",
        )


@router.post("/send-reminders", response_model=list)
async def send_payment_reminders(
    days_overdue: int = Query(30, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list:
    """Send payment reminders.

    Args:
        days_overdue: Days overdue threshold
        db: Database session

    Returns:
        List of reminders sent
    """
    try:
        reminders = await invoicing_agent.send_payment_reminders(db, days_overdue)
        return reminders

    except Exception as e:
        logger.error(f"Error sending reminders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send reminders",
        )


@router.get("/revenue", response_model=RevenueReport)
async def get_revenue_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
) -> RevenueReport:
    """Get revenue report.

    Args:
        start_date: Start date
        end_date: End date
        db: Database session

    Returns:
        Revenue report
    """
    try:
        report = await invoicing_agent.calculate_revenue(db, start_date, end_date)
        return RevenueReport(**report)

    except Exception as e:
        logger.error(f"Error getting revenue report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get revenue report",
        )


@router.get("/analytics", response_model=InvoiceAnalyticsResponse)
async def get_invoicing_analytics(
    db: AsyncSession = Depends(get_db),
) -> InvoiceAnalyticsResponse:
    """Get invoicing analytics.

    Args:
        db: Database session

    Returns:
        Analytics data
    """
    try:
        analytics = await invoicing_agent.get_invoicing_analytics(db)
        return InvoiceAnalyticsResponse(**analytics)

    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get analytics",
        )


# ===== QUICKBOOKS ENDPOINTS =====


@router.post("/quickbooks/connect", response_model=QuickBooksConnectResponse)
async def connect_quickbooks(
    request: QuickBooksConnectRequest,
    db: AsyncSession = Depends(get_db),
) -> QuickBooksConnectResponse:
    """Connect QuickBooks.

    Args:
        request: Connection request
        db: Database session

    Returns:
        Connection status
    """
    try:
        result = await invoicing_agent.connect_quickbooks(
            db, request.auth_code, request.realm_id
        )
        return QuickBooksConnectResponse(**result, connected_at=datetime.utcnow())

    except Exception as e:
        logger.error(f"Error connecting QB: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect QuickBooks",
        )


@router.post("/quickbooks/sync/{invoice_id}", response_model=QuickBooksSyncResponse)
async def sync_invoice_to_quickbooks(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
) -> QuickBooksSyncResponse:
    """Sync invoice to QuickBooks.

    Args:
        invoice_id: Invoice ID
        db: Database session

    Returns:
        Sync result
    """
    try:
        result = await invoicing_agent.sync_invoice_to_quickbooks(db, invoice_id)

        return QuickBooksSyncResponse(
            sync_id=result["sync_log_id"],
            sync_type="invoice",
            status="synced",
            records_processed=1,
            records_failed=0,
            started_at=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"Error syncing invoice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync invoice",
        )


@router.post("/quickbooks/sync-all", response_model=QuickBooksSyncResponse)
async def full_sync_quickbooks(
    db: AsyncSession = Depends(get_db),
) -> QuickBooksSyncResponse:
    """Full QuickBooks sync.

    Args:
        db: Database session

    Returns:
        Sync result
    """
    try:
        result = await invoicing_agent.full_sync_quickbooks(db)

        return QuickBooksSyncResponse(
            sync_id=result["sync_log_id"],
            sync_type="full",
            status="completed",
            records_processed=0,
            records_failed=0,
            started_at=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"Error in full sync: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync QuickBooks",
        )


@router.get("/quickbooks/status", response_model=QuickBooksStatusResponse)
async def get_quickbooks_status(
    db: AsyncSession = Depends(get_db),
) -> QuickBooksStatusResponse:
    """Get QuickBooks connection status.

    Args:
        db: Database session

    Returns:
        Connection status
    """
    try:
        status_data = await invoicing_agent.get_quickbooks_sync_status(db)
        return QuickBooksStatusResponse(**status_data)

    except Exception as e:
        logger.error(f"Error getting QB status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get status",
        )


@router.put("/quickbooks/account-mapping", response_model=dict)
async def map_chart_of_accounts(
    mapping: QuickBooksAccountMapping,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Map chart of accounts.

    Args:
        mapping: Account mapping
        db: Database session

    Returns:
        Mapping confirmation
    """
    try:
        result = await invoicing_agent.map_chart_of_accounts(db, mapping.model_dump())
        return result

    except Exception as e:
        logger.error(f"Error mapping accounts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to map accounts",
        )


# Import datetime for response
from datetime import datetime
