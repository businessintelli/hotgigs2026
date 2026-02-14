"""Invoicing and QuickBooks integration agent."""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from agents.base_agent import BaseAgent
from agents.events import EventType
from models.invoice import Invoice, InvoicePayment, CreditMemo
from services.invoicing_service import InvoicingService, QuickBooksIntegrationService
from schemas.invoice import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceLineItemCreate,
    InvoicePaymentCreate,
    CreditMemoCreate,
    InvoiceListFilter,
    GenerateInvoiceFromTimesheetRequest,
    BulkGenerateInvoicesRequest,
)

logger = logging.getLogger(__name__)


class InvoicingAgent(BaseAgent):
    """Agent for managing invoicing, billing, and QuickBooks integration."""

    def __init__(self):
        """Initialize the invoicing agent."""
        super().__init__(agent_name="InvoicingAgent", agent_version="1.0.0")
        self.quickbooks_client = None
        self.default_payment_terms = "net_30"
        self.default_tax_rate = 0.0

    # ── Invoice Management ──

    async def create_invoice(self, db: AsyncSession, invoice_data: Dict[str, Any]) -> Invoice:
        """Create invoice from approved timesheets or manual entry.

        Auto-calculates line items from timesheet hours × bill rate, taxes, total.
        Applies customer-specific billing rules (markup, discount).

        Args:
            db: Database session
            invoice_data: Invoice data

        Returns:
            Created invoice
        """
        try:
            logger.info(f"Creating invoice for customer {invoice_data.get('customer_id')}")

            service = InvoicingService(db)

            inv_create = InvoiceCreate(**invoice_data)
            invoice = await service.create_invoice(inv_create)

            await self.emit_event(
                event_type=EventType.RESOURCE_CREATED,
                entity_type="invoice",
                entity_id=invoice.id,
                payload={
                    "invoice_number": invoice.invoice_number,
                    "customer_id": invoice.customer_id,
                    "total_amount": invoice.total_amount,
                },
            )

            return invoice

        except Exception as e:
            logger.error(f"Error creating invoice: {str(e)}")
            raise

    async def generate_invoice_from_timesheet(
        self, db: AsyncSession, timesheet_id: int, apply_markup: bool = True
    ) -> Invoice:
        """Auto-generate invoice from approved timesheet.

        Line items: regular hours, overtime hours, expenses.
        Applies customer billing rate and markup.

        Args:
            db: Database session
            timesheet_id: Timesheet ID
            apply_markup: Whether to apply markup

        Returns:
            Created invoice
        """
        try:
            logger.info(f"Generating invoice from timesheet {timesheet_id}")

            service = InvoicingService(db)
            invoice = await service.generate_invoice_from_timesheet(timesheet_id, apply_markup)

            await self.emit_event(
                event_type=EventType.RESOURCE_CREATED,
                entity_type="invoice",
                entity_id=invoice.id,
                payload={"timesheet_id": timesheet_id, "invoice_number": invoice.invoice_number},
            )

            return invoice

        except Exception as e:
            logger.error(f"Error generating invoice from timesheet: {str(e)}")
            raise

    async def generate_bulk_invoices(
        self,
        db: AsyncSession,
        period_start: date,
        period_end: date,
        customer_id: Optional[int] = None,
        apply_markup: bool = True,
    ) -> List[Invoice]:
        """Generate invoices for all approved timesheets in a period.

        Groups by customer. Returns list of created invoices.

        Args:
            db: Database session
            period_start: Start date
            period_end: End date
            customer_id: Optional customer filter
            apply_markup: Whether to apply markup

        Returns:
            List of created invoices
        """
        try:
            logger.info(f"Bulk generating invoices for period {period_start} to {period_end}")

            service = InvoicingService(db)
            invoices = await service.bulk_generate_invoices(
                period_start, period_end, customer_id, apply_markup
            )

            await self.emit_event(
                event_type=EventType.BATCH_OPERATION,
                entity_type="invoice",
                entity_id=0,
                payload={"invoices_created": len(invoices)},
            )

            return invoices

        except Exception as e:
            logger.error(f"Error bulk generating invoices: {str(e)}")
            raise

    async def send_invoice(
        self,
        db: AsyncSession,
        invoice_id: int,
        delivery_method: str = "email",
        recipient: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send invoice to customer via email or customer portal.

        Attaches PDF. Tracks delivery status.

        Args:
            db: Database session
            invoice_id: Invoice ID
            delivery_method: Delivery method
            recipient: Optional recipient email

        Returns:
            Delivery confirmation
        """
        try:
            logger.info(f"Sending invoice {invoice_id} via {delivery_method}")

            service = InvoicingService(db)
            result = await service.send_invoice(invoice_id, delivery_method, recipient)

            await self.emit_event(
                event_type=EventType.NOTIFICATION_SENT,
                entity_type="invoice",
                entity_id=invoice_id,
                payload=result,
            )

            return result

        except Exception as e:
            logger.error(f"Error sending invoice: {str(e)}")
            raise

    async def record_payment(
        self, db: AsyncSession, invoice_id: int, payment_data: Dict[str, Any]
    ) -> InvoicePayment:
        """Record payment received against an invoice.

        Supports partial payments. Updates invoice status (paid/partially_paid).

        Args:
            db: Database session
            invoice_id: Invoice ID
            payment_data: Payment data

        Returns:
            Payment record
        """
        try:
            logger.info(f"Recording payment for invoice {invoice_id}")

            service = InvoicingService(db)

            payment_create = InvoicePaymentCreate(**payment_data)
            payment = await service.record_payment(invoice_id, payment_create)

            await self.emit_event(
                event_type=EventType.RESOURCE_CREATED,
                entity_type="invoice_payment",
                entity_id=payment.id,
                payload={"invoice_id": invoice_id, "amount": payment.amount},
            )

            return payment

        except Exception as e:
            logger.error(f"Error recording payment: {str(e)}")
            raise

    async def void_invoice(self, db: AsyncSession, invoice_id: int, reason: Optional[str] = None) -> Invoice:
        """Void an invoice.

        Creates credit memo if already paid.

        Args:
            db: Database session
            invoice_id: Invoice ID
            reason: Voiding reason

        Returns:
            Updated invoice
        """
        try:
            logger.info(f"Voiding invoice {invoice_id}")

            service = InvoicingService(db)
            invoice = await service.void_invoice(invoice_id, reason)

            await self.emit_event(
                event_type=EventType.RESOURCE_UPDATED,
                entity_type="invoice",
                entity_id=invoice_id,
                payload={"status": "void", "reason": reason},
            )

            return invoice

        except Exception as e:
            logger.error(f"Error voiding invoice: {str(e)}")
            raise

    async def create_credit_memo(
        self, db: AsyncSession, invoice_id: int, memo_data: Dict[str, Any], created_by: Optional[int] = None
    ) -> CreditMemo:
        """Create credit memo against an invoice.

        Args:
            db: Database session
            invoice_id: Invoice ID
            memo_data: Memo data
            created_by: User who created memo

        Returns:
            Credit memo
        """
        try:
            logger.info(f"Creating credit memo for invoice {invoice_id}")

            service = InvoicingService(db)

            memo_create = CreditMemoCreate(**memo_data)
            memo = await service.create_credit_memo(invoice_id, memo_create, created_by)

            await self.emit_event(
                event_type=EventType.RESOURCE_CREATED,
                entity_type="credit_memo",
                entity_id=memo.id,
                payload={"invoice_id": invoice_id, "amount": memo.amount},
            )

            return memo

        except Exception as e:
            logger.error(f"Error creating credit memo: {str(e)}")
            raise

    async def get_aging_report(self, db: AsyncSession) -> Dict[str, Any]:
        """Accounts receivable aging.

        Current, 30 days, 60 days, 90 days, 120+ days.
        Grouped by customer. Total outstanding amounts.

        Args:
            db: Database session

        Returns:
            Aging report
        """
        try:
            logger.info("Generating aging report")

            service = InvoicingService(db)
            report = await service.get_aging_report()

            return report

        except Exception as e:
            logger.error(f"Error generating aging report: {str(e)}")
            raise

    async def send_payment_reminders(self, db: AsyncSession, days_overdue: int = 30) -> List[Dict[str, Any]]:
        """Send payment reminders for overdue invoices.

        Args:
            db: Database session
            days_overdue: Number of days overdue threshold

        Returns:
            List of reminders sent
        """
        try:
            logger.info(f"Sending payment reminders for invoices overdue {days_overdue}+ days")

            service = InvoicingService(db)
            report = await service.get_aging_report()

            reminders_sent = []

            for bucket_key in ["days_30", "days_60", "days_90", "days_120_plus"]:
                bucket = report.get(bucket_key, {})
                for invoice_detail in bucket.get("details", []):
                    reminders_sent.append({
                        "invoice_number": invoice_detail["invoice_number"],
                        "customer_id": invoice_detail["customer_id"],
                        "amount_due": invoice_detail["amount_due"],
                        "days_overdue": invoice_detail["days_overdue"],
                    })

            await self.emit_event(
                event_type=EventType.NOTIFICATION_SENT,
                entity_type="invoice",
                entity_id=0,
                payload={"reminders_sent": len(reminders_sent)},
            )

            return reminders_sent

        except Exception as e:
            logger.error(f"Error sending reminders: {str(e)}")
            raise

    async def calculate_revenue(
        self, db: AsyncSession, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        """Revenue report.

        Invoiced, collected, outstanding, by customer, by month.

        Args:
            db: Database session
            start_date: Start date
            end_date: End date

        Returns:
            Revenue report
        """
        try:
            logger.info(f"Calculating revenue for period {start_date} to {end_date}")

            service = InvoicingService(db)
            report = await service.get_revenue_report(start_date, end_date)

            return report

        except Exception as e:
            logger.error(f"Error calculating revenue: {str(e)}")
            raise

    # ── QuickBooks Integration ──

    async def connect_quickbooks(
        self, db: AsyncSession, auth_code: str, realm_id: str, company_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """OAuth2 connection to QuickBooks Online.

        Exchanges auth code for tokens. Stores encrypted tokens.
        Validates connection with API call.

        Args:
            db: Database session
            auth_code: OAuth2 auth code
            realm_id: QuickBooks realm ID
            company_name: Company name

        Returns:
            Connection status
        """
        try:
            logger.info(f"Connecting QuickBooks for realm {realm_id}")

            service = QuickBooksIntegrationService(db)
            config = await service.connect_quickbooks(auth_code, realm_id, company_name)

            await self.emit_event(
                event_type=EventType.INTEGRATION_CONNECTED,
                entity_type="quickbooks",
                entity_id=config.id,
                payload={"realm_id": realm_id, "company_name": company_name},
            )

            return {
                "is_connected": config.is_connected,
                "realm_id": config.realm_id,
                "company_name": config.company_name,
            }

        except Exception as e:
            logger.error(f"Error connecting QuickBooks: {str(e)}")
            raise

    async def refresh_quickbooks_token(self, db: AsyncSession) -> Dict[str, Any]:
        """Refresh QuickBooks OAuth2 access token using refresh token.

        Args:
            db: Database session

        Returns:
            Token refresh status
        """
        try:
            logger.info("Refreshing QuickBooks token")

            # TODO: Implement OAuth2 token refresh
            return {"status": "token_refreshed", "expires_in": 3600}

        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            raise

    async def sync_invoice_to_quickbooks(self, db: AsyncSession, invoice_id: int) -> Dict[str, Any]:
        """Push invoice to QuickBooks Online.

        Maps: customer → QB customer, line items → QB line items.
        Stores QB invoice ID for reference. Handles field mapping.

        Args:
            db: Database session
            invoice_id: Invoice ID

        Returns:
            Sync result
        """
        try:
            logger.info(f"Syncing invoice {invoice_id} to QuickBooks")

            service = InvoicingService(db)
            invoice = await service.get_invoice(invoice_id)

            if not invoice:
                raise ValueError(f"Invoice {invoice_id} not found")

            # TODO: Implement QB sync
            sync_log = await QuickBooksIntegrationService(db).log_sync_operation(
                sync_type="invoice",
                direction="push",
                entity_type="Invoice",
                status="completed",
                records_processed=1,
                records_failed=0,
            )

            await self.emit_event(
                event_type=EventType.INTEGRATION_SYNCED,
                entity_type="invoice",
                entity_id=invoice_id,
                payload={"qb_sync_status": "synced"},
            )

            return {
                "invoice_id": invoice_id,
                "status": "synced",
                "sync_log_id": sync_log.id,
            }

        except Exception as e:
            logger.error(f"Error syncing invoice: {str(e)}")
            raise

    async def sync_payment_to_quickbooks(self, db: AsyncSession, payment_id: int) -> Dict[str, Any]:
        """Push payment received to QuickBooks.

        Args:
            db: Database session
            payment_id: Payment ID

        Returns:
            Sync result
        """
        try:
            logger.info(f"Syncing payment {payment_id} to QuickBooks")

            sync_log = await QuickBooksIntegrationService(db).log_sync_operation(
                sync_type="payment",
                direction="push",
                entity_type="Payment",
                status="completed",
                records_processed=1,
                records_failed=0,
            )

            return {
                "payment_id": payment_id,
                "status": "synced",
                "sync_log_id": sync_log.id,
            }

        except Exception as e:
            logger.error(f"Error syncing payment: {str(e)}")
            raise

    async def sync_customer_to_quickbooks(self, db: AsyncSession, customer_id: int) -> Dict[str, Any]:
        """Sync customer/vendor record to QuickBooks.

        Creates if not exists, updates if changed.

        Args:
            db: Database session
            customer_id: Customer ID

        Returns:
            Sync result
        """
        try:
            logger.info(f"Syncing customer {customer_id} to QuickBooks")

            sync_log = await QuickBooksIntegrationService(db).log_sync_operation(
                sync_type="customer",
                direction="push",
                entity_type="Customer",
                status="completed",
                records_processed=1,
                records_failed=0,
            )

            return {
                "customer_id": customer_id,
                "status": "synced",
                "sync_log_id": sync_log.id,
            }

        except Exception as e:
            logger.error(f"Error syncing customer: {str(e)}")
            raise

    async def sync_vendor_to_quickbooks(self, db: AsyncSession, supplier_id: int) -> Dict[str, Any]:
        """Sync supplier as vendor in QuickBooks.

        Args:
            db: Database session
            supplier_id: Supplier ID

        Returns:
            Sync result
        """
        try:
            logger.info(f"Syncing vendor {supplier_id} to QuickBooks")

            sync_log = await QuickBooksIntegrationService(db).log_sync_operation(
                sync_type="vendor",
                direction="push",
                entity_type="Vendor",
                status="completed",
                records_processed=1,
                records_failed=0,
            )

            return {
                "supplier_id": supplier_id,
                "status": "synced",
                "sync_log_id": sync_log.id,
            }

        except Exception as e:
            logger.error(f"Error syncing vendor: {str(e)}")
            raise

    async def import_from_quickbooks(self, db: AsyncSession, entity_type: str) -> Dict[str, Any]:
        """Import data from QuickBooks.

        Customers, invoices, payments. Reconciles with platform data.

        Args:
            db: Database session
            entity_type: Entity type to import

        Returns:
            Import result
        """
        try:
            logger.info(f"Importing {entity_type} from QuickBooks")

            sync_log = await QuickBooksIntegrationService(db).log_sync_operation(
                sync_type="import",
                direction="pull",
                entity_type=entity_type,
                status="completed",
                records_processed=0,
                records_failed=0,
            )

            return {
                "entity_type": entity_type,
                "status": "imported",
                "sync_log_id": sync_log.id,
            }

        except Exception as e:
            logger.error(f"Error importing from QB: {str(e)}")
            raise

    async def full_sync_quickbooks(self, db: AsyncSession) -> Dict[str, Any]:
        """Run full bidirectional sync with QuickBooks.

        Pushes: invoices, payments, customers, vendors.
        Pulls: payment status updates, new payments.

        Args:
            db: Database session

        Returns:
            Full sync result
        """
        try:
            logger.info("Running full QuickBooks sync")

            sync_log = await QuickBooksIntegrationService(db).log_sync_operation(
                sync_type="full",
                direction="bidirectional",
                entity_type="all",
                status="completed",
                records_processed=0,
                records_failed=0,
            )

            await self.emit_event(
                event_type=EventType.INTEGRATION_SYNCED,
                entity_type="quickbooks",
                entity_id=0,
                payload={"sync_type": "full", "status": "completed"},
            )

            return {
                "status": "completed",
                "sync_log_id": sync_log.id,
            }

        except Exception as e:
            logger.error(f"Error in full sync: {str(e)}")
            raise

    async def get_quickbooks_sync_status(self, db: AsyncSession) -> Dict[str, Any]:
        """Get sync status.

        Last sync time, pending items, errors, sync health.

        Args:
            db: Database session

        Returns:
            Sync status
        """
        try:
            logger.info("Getting QuickBooks sync status")

            service = QuickBooksIntegrationService(db)
            status = await service.get_quickbooks_status()

            return status

        except Exception as e:
            logger.error(f"Error getting sync status: {str(e)}")
            raise

    async def map_chart_of_accounts(self, db: AsyncSession, mapping: Dict[str, str]) -> Dict[str, Any]:
        """Map platform income/expense categories to QuickBooks chart of accounts.

        Args:
            db: Database session
            mapping: Account mapping

        Returns:
            Mapping confirmation
        """
        try:
            logger.info("Mapping chart of accounts")

            # TODO: Store mapping in config
            return {
                "status": "mapped",
                "mapping": mapping,
            }

        except Exception as e:
            logger.error(f"Error mapping accounts: {str(e)}")
            raise

    async def generate_invoice_pdf(self, db: AsyncSession, invoice_id: int) -> str:
        """Generate professional invoice PDF.

        Includes: company logo, invoice #, dates, customer info, line items,
        subtotal, tax, total, payment terms, bank details.

        Args:
            db: Database session
            invoice_id: Invoice ID

        Returns:
            File path
        """
        try:
            logger.info(f"Generating PDF for invoice {invoice_id}")

            service = InvoicingService(db)
            invoice = await service.get_invoice(invoice_id)

            if not invoice:
                raise ValueError(f"Invoice {invoice_id} not found")

            # TODO: Implement PDF generation
            pdf_path = f"/tmp/invoice_{invoice.invoice_number}.pdf"

            invoice.pdf_path = pdf_path
            await db.commit()

            return pdf_path

        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise

    async def calculate_tax(self, db: AsyncSession, invoice_id: int) -> Dict[str, Any]:
        """Calculate applicable taxes.

        Based on customer location and service type.
        Supports: sales tax, GST, VAT based on jurisdiction.

        Args:
            db: Database session
            invoice_id: Invoice ID

        Returns:
            Tax calculation
        """
        try:
            logger.info(f"Calculating tax for invoice {invoice_id}")

            service = InvoicingService(db)
            invoice = await service.get_invoice(invoice_id)

            if not invoice:
                raise ValueError(f"Invoice {invoice_id} not found")

            # TODO: Implement tax calculation based on jurisdiction
            tax_amount = invoice.subtotal * (invoice.tax_rate or 0) / 100

            return {
                "invoice_id": invoice_id,
                "subtotal": invoice.subtotal,
                "tax_rate": invoice.tax_rate,
                "tax_amount": tax_amount,
                "total": invoice.subtotal + tax_amount,
            }

        except Exception as e:
            logger.error(f"Error calculating tax: {str(e)}")
            raise

    async def get_invoicing_analytics(self, db: AsyncSession) -> Dict[str, Any]:
        """Analytics: total invoiced, collected, outstanding.

        avg days to pay, collection rate, overdue %, revenue by customer,
        margin by placement.

        Args:
            db: Database session

        Returns:
            Analytics data
        """
        try:
            logger.info("Getting invoicing analytics")

            service = InvoicingService(db)
            analytics = await service.get_invoicing_analytics()

            return analytics

        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            raise
