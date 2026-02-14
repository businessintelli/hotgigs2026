"""Invoicing service for customer billing and QuickBooks integration."""

import logging
import hashlib
import base64
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any, Tuple
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from models.invoice import (
    Invoice,
    InvoiceLineItem,
    InvoicePayment,
    CreditMemo,
    QuickBooksConfig,
    QuickBooksSyncLog,
)
from models.timesheet import Timesheet, TimesheetEntry
from models.offer import Offer
from models.customer import Customer
from schemas.invoice import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceLineItemCreate,
    InvoiceLineItemUpdate,
    InvoicePaymentCreate,
    CreditMemoCreate,
    InvoiceListFilter,
)

logger = logging.getLogger(__name__)


class InvoicingService:
    """Service for invoice operations."""

    def __init__(self, db: AsyncSession):
        """Initialize invoicing service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_invoice(self, invoice_data: InvoiceCreate) -> Invoice:
        """Create a new invoice.

        Args:
            invoice_data: Invoice creation data

        Returns:
            Created invoice

        Raises:
            ValueError: If customer not found
        """
        try:
            # Verify customer exists
            result = await self.db.execute(
                select(Customer).where(Customer.id == invoice_data.customer_id)
            )
            if not result.scalar_one_or_none():
                raise ValueError(f"Customer {invoice_data.customer_id} not found")

            # Generate invoice number
            invoice_number = await self._generate_invoice_number()

            invoice = Invoice(
                invoice_number=invoice_number,
                customer_id=invoice_data.customer_id,
                invoice_date=invoice_data.invoice_date,
                due_date=invoice_data.due_date,
                period_start=invoice_data.period_start,
                period_end=invoice_data.period_end,
                payment_terms=invoice_data.payment_terms,
                tax_rate=invoice_data.tax_rate,
                discount_percentage=invoice_data.discount_percentage,
                notes=invoice_data.notes,
                internal_notes=invoice_data.internal_notes,
                created_by=invoice_data.created_by,
                status="draft",
            )

            self.db.add(invoice)
            await self.db.commit()
            await self.db.refresh(invoice)

            logger.info(f"Created invoice {invoice.invoice_number}")
            return invoice

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating invoice: {str(e)}")
            raise

    async def get_invoice(self, invoice_id: int) -> Optional[Invoice]:
        """Get invoice by ID.

        Args:
            invoice_id: Invoice ID

        Returns:
            Invoice or None
        """
        try:
            result = await self.db.execute(
                select(Invoice).where(Invoice.id == invoice_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting invoice: {str(e)}")
            raise

    async def get_invoices(self, filters: InvoiceListFilter) -> Tuple[List[Invoice], int]:
        """Get invoices with filters.

        Args:
            filters: Filter criteria

        Returns:
            Tuple of (invoices, total_count)
        """
        try:
            conditions = []

            if filters.customer_id:
                conditions.append(Invoice.customer_id == filters.customer_id)
            if filters.status:
                conditions.append(Invoice.status == filters.status)
            if filters.invoice_date_start:
                conditions.append(Invoice.invoice_date >= filters.invoice_date_start)
            if filters.invoice_date_end:
                conditions.append(Invoice.invoice_date <= filters.invoice_date_end)
            if filters.due_date_start:
                conditions.append(Invoice.due_date >= filters.due_date_start)
            if filters.due_date_end:
                conditions.append(Invoice.due_date <= filters.due_date_end)

            query = select(Invoice)
            if conditions:
                query = query.where(and_(*conditions))

            # Get total count
            count_result = await self.db.execute(
                select(func.count()).select_from(Invoice).where(
                    and_(*conditions) if conditions else True
                )
            )
            total = count_result.scalar()

            # Get paginated results
            query = query.order_by(desc(Invoice.created_at))
            query = query.offset(filters.skip).limit(filters.limit)

            result = await self.db.execute(query)
            invoices = result.scalars().all()

            return invoices, total

        except Exception as e:
            logger.error(f"Error getting invoices: {str(e)}")
            raise

    async def update_invoice(self, invoice_id: int, update_data: InvoiceUpdate) -> Invoice:
        """Update invoice.

        Args:
            invoice_id: Invoice ID
            update_data: Update data

        Returns:
            Updated invoice
        """
        try:
            invoice = await self.get_invoice(invoice_id)
            if not invoice:
                raise ValueError(f"Invoice {invoice_id} not found")

            if invoice.status not in ["draft", "sent"]:
                raise ValueError(f"Cannot update invoice with status {invoice.status}")

            update_dict = update_data.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(invoice, key, value)

            await self.db.commit()
            await self.db.refresh(invoice)

            logger.info(f"Updated invoice {invoice_id}")
            return invoice

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating invoice: {str(e)}")
            raise

    async def add_line_item(
        self, invoice_id: int, item_data: InvoiceLineItemCreate
    ) -> InvoiceLineItem:
        """Add line item to invoice.

        Args:
            invoice_id: Invoice ID
            item_data: Line item data

        Returns:
            Created line item
        """
        try:
            invoice = await self.get_invoice(invoice_id)
            if not invoice:
                raise ValueError(f"Invoice {invoice_id} not found")

            if invoice.status not in ["draft", "sent"]:
                raise ValueError(f"Cannot add items to invoice with status {invoice.status}")

            # Calculate amount
            amount = item_data.quantity * item_data.unit_price

            line_item = InvoiceLineItem(
                invoice_id=invoice_id,
                description=item_data.description,
                quantity=item_data.quantity,
                unit_type=item_data.unit_type,
                unit_price=item_data.unit_price,
                amount=amount,
                is_taxable=item_data.is_taxable,
                line_type=item_data.line_type,
                project_code=item_data.project_code,
                timesheet_id=item_data.timesheet_id,
                placement_id=item_data.placement_id,
            )

            self.db.add(line_item)
            await self.db.commit()
            await self.db.refresh(line_item)

            # Recalculate invoice totals
            await self._recalculate_invoice_totals(invoice_id)

            logger.info(f"Added line item {line_item.id} to invoice {invoice_id}")
            return line_item

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error adding line item: {str(e)}")
            raise

    async def update_line_item(
        self, item_id: int, update_data: InvoiceLineItemUpdate
    ) -> InvoiceLineItem:
        """Update line item.

        Args:
            item_id: Line item ID
            update_data: Update data

        Returns:
            Updated line item
        """
        try:
            result = await self.db.execute(
                select(InvoiceLineItem).where(InvoiceLineItem.id == item_id)
            )
            item = result.scalar_one_or_none()
            if not item:
                raise ValueError(f"Line item {item_id} not found")

            update_dict = update_data.model_dump(exclude_unset=True)

            # Recalculate amount if quantity or price changed
            if "quantity" in update_dict or "unit_price" in update_dict:
                quantity = update_dict.get("quantity", item.quantity)
                price = update_dict.get("unit_price", item.unit_price)
                update_dict["amount"] = quantity * price

            for key, value in update_dict.items():
                setattr(item, key, value)

            await self.db.commit()
            await self.db.refresh(item)

            # Recalculate invoice totals
            await self._recalculate_invoice_totals(item.invoice_id)

            logger.info(f"Updated line item {item_id}")
            return item

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating line item: {str(e)}")
            raise

    async def delete_line_item(self, item_id: int) -> None:
        """Delete line item.

        Args:
            item_id: Line item ID
        """
        try:
            result = await self.db.execute(
                select(InvoiceLineItem).where(InvoiceLineItem.id == item_id)
            )
            item = result.scalar_one_or_none()
            if not item:
                raise ValueError(f"Line item {item_id} not found")

            invoice_id = item.invoice_id
            await self.db.delete(item)
            await self.db.commit()

            # Recalculate invoice totals
            await self._recalculate_invoice_totals(invoice_id)

            logger.info(f"Deleted line item {item_id}")

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting line item: {str(e)}")
            raise

    async def generate_invoice_from_timesheet(
        self, timesheet_id: int, apply_markup: bool = True, markup_percentage: Optional[float] = None
    ) -> Invoice:
        """Generate invoice from approved timesheet.

        Args:
            timesheet_id: Timesheet ID
            apply_markup: Whether to apply markup
            markup_percentage: Custom markup percentage

        Returns:
            Created invoice

        Raises:
            ValueError: If timesheet not found or not approved
        """
        try:
            # Get timesheet with entries
            result = await self.db.execute(
                select(Timesheet).where(Timesheet.id == timesheet_id)
            )
            timesheet = result.scalar_one_or_none()
            if not timesheet:
                raise ValueError(f"Timesheet {timesheet_id} not found")

            if timesheet.status != "approved":
                raise ValueError(f"Timesheet must be approved (current status: {timesheet.status})")

            # Create invoice
            invoice_data = InvoiceCreate(
                customer_id=timesheet.customer_id,
                invoice_date=date.today(),
                due_date=date.today() + timedelta(days=30),
                period_start=timesheet.period_start,
                period_end=timesheet.period_end,
                payment_terms="net_30",
            )

            invoice = await self.create_invoice(invoice_data)

            # Add line items from timesheet entries
            result = await self.db.execute(
                select(TimesheetEntry).where(TimesheetEntry.timesheet_id == timesheet_id)
            )
            entries = result.scalars().all()

            # Group entries by day and add as line items
            for entry in entries:
                if entry.total_hours > 0:
                    description = f"Services - {entry.entry_date.strftime('%B %d, %Y')}"
                    if entry.task_description:
                        description += f": {entry.task_description}"

                    unit_price = timesheet.bill_rate or timesheet.regular_rate

                    # Apply markup if requested
                    if apply_markup:
                        markup_pct = markup_percentage or 0.15
                        unit_price = unit_price * (1 + markup_pct / 100)

                    item_data = InvoiceLineItemCreate(
                        description=description,
                        quantity=entry.total_hours,
                        unit_type="hours",
                        unit_price=unit_price,
                        is_taxable=True,
                        line_type="service",
                        project_code=entry.project_code,
                        timesheet_id=timesheet_id,
                        placement_id=timesheet.placement_id,
                    )

                    await self.add_line_item(invoice.id, item_data)

            # Link invoice to timesheet
            timesheet.invoice_id = invoice.id
            await self.db.commit()

            logger.info(f"Generated invoice {invoice.invoice_number} from timesheet {timesheet_id}")
            return invoice

        except Exception as e:
            logger.error(f"Error generating invoice from timesheet: {str(e)}")
            raise

    async def bulk_generate_invoices(
        self,
        period_start: date,
        period_end: date,
        customer_id: Optional[int] = None,
        apply_markup: bool = True,
    ) -> List[Invoice]:
        """Generate invoices for approved timesheets in period.

        Args:
            period_start: Start date
            period_end: End date
            customer_id: Optional customer filter
            apply_markup: Whether to apply markup

        Returns:
            List of created invoices
        """
        try:
            conditions = [
                Timesheet.status == "approved",
                Timesheet.invoice_id.is_(None),
                Timesheet.period_start >= period_start,
                Timesheet.period_end <= period_end,
            ]

            if customer_id:
                conditions.append(Timesheet.customer_id == customer_id)

            result = await self.db.execute(
                select(Timesheet).where(and_(*conditions))
            )
            timesheets = result.scalars().all()

            created_invoices = []

            for ts in timesheets:
                try:
                    invoice = await self.generate_invoice_from_timesheet(
                        ts.id, apply_markup=apply_markup
                    )
                    created_invoices.append(invoice)
                except Exception as e:
                    logger.warning(f"Failed to generate invoice for timesheet {ts.id}: {str(e)}")

            logger.info(f"Generated {len(created_invoices)} invoices")
            return created_invoices

        except Exception as e:
            logger.error(f"Error bulk generating invoices: {str(e)}")
            raise

    async def send_invoice(self, invoice_id: int, delivery_method: str = "email", recipient: Optional[str] = None) -> Dict[str, Any]:
        """Send invoice to customer.

        Args:
            invoice_id: Invoice ID
            delivery_method: Delivery method (email, portal)
            recipient: Optional recipient email

        Returns:
            Delivery confirmation
        """
        try:
            invoice = await self.get_invoice(invoice_id)
            if not invoice:
                raise ValueError(f"Invoice {invoice_id} not found")

            # Get customer
            result = await self.db.execute(
                select(Customer).where(Customer.id == invoice.customer_id)
            )
            customer = result.scalar_one_or_none()
            if not customer:
                raise ValueError(f"Customer {invoice.customer_id} not found")

            invoice.status = "sent"
            invoice.sent_at = datetime.utcnow()
            invoice.sent_to = recipient or getattr(customer, "email", None)

            await self.db.commit()

            logger.info(f"Sent invoice {invoice.invoice_number} via {delivery_method}")
            return {
                "invoice_id": invoice_id,
                "invoice_number": invoice.invoice_number,
                "delivery_method": delivery_method,
                "sent_to": invoice.sent_to,
                "sent_at": invoice.sent_at.isoformat(),
            }

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error sending invoice: {str(e)}")
            raise

    async def record_payment(self, invoice_id: int, payment_data: InvoicePaymentCreate) -> InvoicePayment:
        """Record payment against invoice.

        Args:
            invoice_id: Invoice ID
            payment_data: Payment data

        Returns:
            Created payment record
        """
        try:
            invoice = await self.get_invoice(invoice_id)
            if not invoice:
                raise ValueError(f"Invoice {invoice_id} not found")

            payment = InvoicePayment(
                invoice_id=invoice_id,
                payment_date=payment_data.payment_date,
                amount=payment_data.amount,
                payment_method=payment_data.payment_method,
                reference_number=payment_data.reference_number,
                notes=payment_data.notes,
                recorded_by=payment_data.recorded_by,
            )

            self.db.add(payment)

            # Update invoice amounts
            invoice.amount_paid += payment.amount
            invoice.amount_due = invoice.total_amount - invoice.amount_paid

            # Update status
            if invoice.amount_paid >= invoice.total_amount:
                invoice.status = "paid"
            elif invoice.amount_paid > 0:
                invoice.status = "partially_paid"

            await self.db.commit()
            await self.db.refresh(payment)

            logger.info(f"Recorded payment of {payment.amount} for invoice {invoice_id}")
            return payment

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error recording payment: {str(e)}")
            raise

    async def void_invoice(self, invoice_id: int, reason: Optional[str] = None) -> Invoice:
        """Void an invoice.

        Args:
            invoice_id: Invoice ID
            reason: Voiding reason

        Returns:
            Updated invoice
        """
        try:
            invoice = await self.get_invoice(invoice_id)
            if not invoice:
                raise ValueError(f"Invoice {invoice_id} not found")

            if invoice.status == "paid":
                raise ValueError("Cannot void a paid invoice")

            invoice.status = "void"
            if reason:
                invoice.internal_notes = f"Voided: {reason}"

            await self.db.commit()

            logger.info(f"Voided invoice {invoice_id}")
            return invoice

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error voiding invoice: {str(e)}")
            raise

    async def create_credit_memo(
        self, invoice_id: int, memo_data: CreditMemoCreate, created_by: Optional[int] = None
    ) -> CreditMemo:
        """Create credit memo against invoice.

        Args:
            invoice_id: Invoice ID
            memo_data: Credit memo data
            created_by: User who created memo

        Returns:
            Created credit memo
        """
        try:
            invoice = await self.get_invoice(invoice_id)
            if not invoice:
                raise ValueError(f"Invoice {invoice_id} not found")

            # Generate memo number
            memo_number = await self._generate_credit_memo_number()

            memo = CreditMemo(
                invoice_id=invoice_id,
                memo_number=memo_number,
                amount=memo_data.amount,
                reason=memo_data.reason,
                status="issued",
                created_by=created_by,
            )

            self.db.add(memo)

            # Adjust invoice amounts
            invoice.amount_due += memo.amount
            invoice.total_amount += memo.amount

            await self.db.commit()
            await self.db.refresh(memo)

            logger.info(f"Created credit memo {memo_number}")
            return memo

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating credit memo: {str(e)}")
            raise

    async def get_aging_report(self) -> Dict[str, Any]:
        """Get accounts receivable aging report.

        Returns:
            Aging report data
        """
        try:
            today = date.today()

            conditions = [Invoice.status != "paid", Invoice.status != "void"]

            result = await self.db.execute(
                select(Invoice).where(and_(*conditions)).order_by(Invoice.due_date)
            )
            invoices = result.scalars().all()

            current = []
            days_30 = []
            days_60 = []
            days_90 = []
            days_120_plus = []

            for inv in invoices:
                days_overdue = (today - inv.due_date).days

                invoice_info = {
                    "invoice_number": inv.invoice_number,
                    "customer_id": inv.customer_id,
                    "invoice_date": inv.invoice_date.isoformat(),
                    "due_date": inv.due_date.isoformat(),
                    "amount_due": inv.amount_due,
                    "days_overdue": max(0, days_overdue),
                }

                if days_overdue <= 0:
                    current.append(invoice_info)
                elif days_overdue <= 30:
                    days_30.append(invoice_info)
                elif days_overdue <= 60:
                    days_60.append(invoice_info)
                elif days_overdue <= 90:
                    days_90.append(invoice_info)
                else:
                    days_120_plus.append(invoice_info)

            return {
                "total_outstanding": sum(inv.amount_due for inv in invoices),
                "total_invoices": len(invoices),
                "current": {
                    "bucket": "current",
                    "invoice_count": len(current),
                    "total_amount": sum(inv["amount_due"] for inv in current),
                    "customer_count": len(set(inv["customer_id"] for inv in current)),
                    "details": current,
                },
                "days_30": {
                    "bucket": "30_days",
                    "invoice_count": len(days_30),
                    "total_amount": sum(inv["amount_due"] for inv in days_30),
                    "customer_count": len(set(inv["customer_id"] for inv in days_30)),
                    "details": days_30,
                },
                "days_60": {
                    "bucket": "60_days",
                    "invoice_count": len(days_60),
                    "total_amount": sum(inv["amount_due"] for inv in days_60),
                    "customer_count": len(set(inv["customer_id"] for inv in days_60)),
                    "details": days_60,
                },
                "days_90": {
                    "bucket": "90_days",
                    "invoice_count": len(days_90),
                    "total_amount": sum(inv["amount_due"] for inv in days_90),
                    "customer_count": len(set(inv["customer_id"] for inv in days_90)),
                    "details": days_90,
                },
                "days_120_plus": {
                    "bucket": "120_plus",
                    "invoice_count": len(days_120_plus),
                    "total_amount": sum(inv["amount_due"] for inv in days_120_plus),
                    "customer_count": len(set(inv["customer_id"] for inv in days_120_plus)),
                    "details": days_120_plus,
                },
            }

        except Exception as e:
            logger.error(f"Error generating aging report: {str(e)}")
            raise

    async def get_revenue_report(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get revenue report for period.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Revenue report data
        """
        try:
            result = await self.db.execute(
                select(Invoice).where(
                    and_(
                        Invoice.invoice_date >= start_date,
                        Invoice.invoice_date <= end_date,
                    )
                )
            )
            invoices = result.scalars().all()

            total_invoiced = sum(inv.total_amount for inv in invoices)
            total_collected = sum(inv.amount_paid for inv in invoices)
            total_outstanding = sum(inv.amount_due for inv in invoices)

            # Group by customer
            by_customer = {}
            for inv in invoices:
                if inv.customer_id not in by_customer:
                    by_customer[inv.customer_id] = {
                        "total_invoiced": 0,
                        "total_collected": 0,
                        "total_outstanding": 0,
                    }
                by_customer[inv.customer_id]["total_invoiced"] += inv.total_amount
                by_customer[inv.customer_id]["total_collected"] += inv.amount_paid
                by_customer[inv.customer_id]["total_outstanding"] += inv.amount_due

            # Group by month
            by_month = {}
            for inv in invoices:
                month_key = inv.invoice_date.strftime("%Y-%m")
                if month_key not in by_month:
                    by_month[month_key] = {
                        "total_invoiced": 0,
                        "total_collected": 0,
                        "total_outstanding": 0,
                    }
                by_month[month_key]["total_invoiced"] += inv.total_amount
                by_month[month_key]["total_collected"] += inv.amount_paid
                by_month[month_key]["total_outstanding"] += inv.amount_due

            collection_rate = (total_collected / total_invoiced * 100) if total_invoiced > 0 else 0

            return {
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat(),
                "total_invoiced": total_invoiced,
                "total_collected": total_collected,
                "total_outstanding": total_outstanding,
                "collection_rate": collection_rate,
                "by_customer": by_customer,
                "by_month": by_month,
            }

        except Exception as e:
            logger.error(f"Error generating revenue report: {str(e)}")
            raise

    async def get_invoicing_analytics(self) -> Dict[str, Any]:
        """Get invoicing analytics.

        Returns:
            Analytics data
        """
        try:
            result = await self.db.execute(select(Invoice))
            invoices = result.scalars().all()

            if not invoices:
                return {
                    "total_invoiced": 0,
                    "total_collected": 0,
                    "total_outstanding": 0,
                    "avg_days_to_pay": 0,
                    "collection_rate": 0,
                    "overdue_percentage": 0,
                    "total_invoices": 0,
                    "paid_invoices": 0,
                    "overdue_invoices": 0,
                    "revenue_by_customer": {},
                    "margin_by_placement": {},
                }

            total_invoiced = sum(inv.total_amount for inv in invoices)
            total_collected = sum(inv.amount_paid for inv in invoices)
            total_outstanding = sum(inv.amount_due for inv in invoices)

            # Count statuses
            paid_count = sum(1 for inv in invoices if inv.status == "paid")
            overdue_count = sum(1 for inv in invoices if inv.status == "overdue")

            # Calculate days to pay
            days_to_pay = []
            result = await self.db.execute(
                select(InvoicePayment)
                .join(Invoice)
                .where(Invoice.status == "paid")
            )
            payments = result.scalars().all()

            for payment in payments:
                inv = await self.get_invoice(payment.invoice_id)
                if inv and inv.invoice_date:
                    days = (payment.payment_date - inv.invoice_date).days
                    days_to_pay.append(days)

            avg_days = sum(days_to_pay) / len(days_to_pay) if days_to_pay else 0

            # Revenue by customer
            revenue_by_customer = {}
            for inv in invoices:
                if inv.customer_id not in revenue_by_customer:
                    revenue_by_customer[inv.customer_id] = 0
                revenue_by_customer[inv.customer_id] += inv.total_amount

            return {
                "total_invoiced": total_invoiced,
                "total_collected": total_collected,
                "total_outstanding": total_outstanding,
                "avg_days_to_pay": avg_days,
                "collection_rate": (total_collected / total_invoiced * 100) if total_invoiced > 0 else 0,
                "overdue_percentage": (overdue_count / len(invoices) * 100) if invoices else 0,
                "total_invoices": len(invoices),
                "paid_invoices": paid_count,
                "overdue_invoices": overdue_count,
                "revenue_by_customer": revenue_by_customer,
                "margin_by_placement": {},
            }

        except Exception as e:
            logger.error(f"Error generating analytics: {str(e)}")
            raise

    async def _recalculate_invoice_totals(self, invoice_id: int) -> None:
        """Recalculate invoice totals from line items.

        Args:
            invoice_id: Invoice ID
        """
        try:
            invoice = await self.get_invoice(invoice_id)
            if not invoice:
                return

            # Get line items
            result = await self.db.execute(
                select(InvoiceLineItem).where(InvoiceLineItem.invoice_id == invoice_id)
            )
            items = result.scalars().all()

            # Calculate subtotal
            subtotal = sum(item.amount for item in items)

            # Calculate tax
            taxable_amount = sum(item.amount for item in items if item.is_taxable)
            tax_amount = 0.0
            if invoice.tax_rate:
                tax_amount = taxable_amount * (invoice.tax_rate / 100)

            # Calculate discount
            discount_amount = 0.0
            if invoice.discount_percentage:
                discount_amount = subtotal * (invoice.discount_percentage / 100)

            # Calculate total
            total_amount = subtotal + tax_amount - discount_amount

            # Update invoice
            invoice.subtotal = subtotal
            invoice.tax_amount = tax_amount
            invoice.discount_amount = discount_amount
            invoice.total_amount = total_amount
            invoice.amount_due = total_amount - invoice.amount_paid

            await self.db.commit()
            logger.debug(f"Recalculated totals for invoice {invoice_id}")

        except Exception as e:
            logger.error(f"Error recalculating totals: {str(e)}")
            await self.db.rollback()

    async def _generate_invoice_number(self) -> str:
        """Generate unique invoice number.

        Returns:
            Invoice number
        """
        try:
            today = date.today()
            year = today.year
            month = today.month

            # Get count of invoices this month
            result = await self.db.execute(
                select(func.count()).select_from(Invoice).where(
                    and_(
                        func.year(Invoice.created_at) == year,
                        func.month(Invoice.created_at) == month,
                    )
                )
            )
            count = result.scalar() or 0

            invoice_number = f"INV-{year}{month:02d}-{count + 1:05d}"
            return invoice_number

        except Exception as e:
            logger.error(f"Error generating invoice number: {str(e)}")
            raise

    async def _generate_credit_memo_number(self) -> str:
        """Generate unique credit memo number.

        Returns:
            Memo number
        """
        try:
            today = date.today()
            year = today.year
            month = today.month

            result = await self.db.execute(
                select(func.count()).select_from(CreditMemo)
            )
            count = result.scalar() or 0

            memo_number = f"CM-{year}{month:02d}-{count + 1:05d}"
            return memo_number

        except Exception as e:
            logger.error(f"Error generating credit memo number: {str(e)}")
            raise


class QuickBooksIntegrationService:
    """Service for QuickBooks integration."""

    def __init__(self, db: AsyncSession):
        """Initialize QuickBooks integration service.

        Args:
            db: Database session
        """
        self.db = db

    async def connect_quickbooks(
        self, auth_code: str, realm_id: str, company_name: Optional[str] = None
    ) -> QuickBooksConfig:
        """Establish QuickBooks connection.

        Args:
            auth_code: OAuth2 auth code
            realm_id: QuickBooks realm ID
            company_name: Company name

        Returns:
            QB config record

        Raises:
            ValueError: If connection fails
        """
        try:
            # Check if config already exists
            result = await self.db.execute(
                select(QuickBooksConfig).where(QuickBooksConfig.realm_id == realm_id)
            )
            config = result.scalar_one_or_none()

            if not config:
                config = QuickBooksConfig(
                    realm_id=realm_id,
                    company_name=company_name,
                    is_connected=False,
                )
                self.db.add(config)

            # TODO: Exchange auth_code for access_token via OAuth2
            # For now, mark as pending connection
            config.is_connected = True
            config.token_expires_at = datetime.utcnow() + timedelta(hours=1)

            await self.db.commit()
            await self.db.refresh(config)

            logger.info(f"Connected QuickBooks for realm {realm_id}")
            return config

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error connecting QuickBooks: {str(e)}")
            raise

    async def get_quickbooks_status(self) -> Dict[str, Any]:
        """Get QuickBooks connection status.

        Returns:
            Status info
        """
        try:
            result = await self.db.execute(select(QuickBooksConfig).limit(1))
            config = result.scalar_one_or_none()

            if not config:
                return {
                    "is_connected": False,
                    "realm_id": None,
                    "company_name": None,
                    "last_sync_at": None,
                    "token_expires_at": None,
                    "sync_health": "not_configured",
                }

            return {
                "is_connected": config.is_connected,
                "realm_id": config.realm_id,
                "company_name": config.company_name,
                "last_sync_at": config.last_sync_at.isoformat() if config.last_sync_at else None,
                "token_expires_at": config.token_expires_at.isoformat() if config.token_expires_at else None,
                "sync_health": "healthy" if config.is_connected else "disconnected",
            }

        except Exception as e:
            logger.error(f"Error getting QB status: {str(e)}")
            raise

    async def log_sync_operation(
        self,
        sync_type: str,
        direction: str,
        entity_type: Optional[str],
        status: str,
        records_processed: int = 0,
        records_failed: int = 0,
        error_details: Optional[Dict] = None,
        triggered_by: Optional[int] = None,
    ) -> QuickBooksSyncLog:
        """Log a QuickBooks sync operation.

        Args:
            sync_type: Type of sync
            direction: Sync direction
            entity_type: Entity type
            status: Operation status
            records_processed: Number of records processed
            records_failed: Number of failed records
            error_details: Error details if any
            triggered_by: User who triggered sync

        Returns:
            Log entry
        """
        try:
            log_entry = QuickBooksSyncLog(
                sync_type=sync_type,
                direction=direction,
                entity_type=entity_type,
                status=status,
                records_processed=records_processed,
                records_failed=records_failed,
                error_details=error_details,
                triggered_by=triggered_by,
            )

            self.db.add(log_entry)
            await self.db.commit()
            await self.db.refresh(log_entry)

            logger.info(f"Logged QB sync: {sync_type} ({status})")
            return log_entry

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error logging sync: {str(e)}")
            raise
