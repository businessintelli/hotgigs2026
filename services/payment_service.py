"""Payment service for managing payments and reconciliation."""

import logging
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from decimal import Decimal
from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.payment import Payment, PaymentMethod, PaymentSchedule, PaymentReconciliation
from schemas.payment import (
    PaymentCreate,
    PaymentUpdate,
    PaymentMethodCreate,
    PaymentScheduleCreate,
    PaymentScheduleUpdate,
)

logger = logging.getLogger(__name__)


class PaymentService:
    """Service for payment management."""

    def __init__(self, db: AsyncSession):
        """Initialize payment service.

        Args:
            db: Async database session
        """
        self.db = db

    # Payment management

    async def create_payment(self, payment_data: PaymentCreate) -> Payment:
        """Create payment record.

        Args:
            payment_data: Payment creation data

        Returns:
            Created payment

        Raises:
            ValueError: If validation fails
        """
        # Validate amounts
        if payment_data.gross_amount <= 0:
            raise ValueError("Gross amount must be greater than zero")

        total_deductions = payment_data.tax_withholding + payment_data.deductions
        if total_deductions >= payment_data.gross_amount:
            raise ValueError("Deductions cannot equal or exceed gross amount")

        net_amount = payment_data.gross_amount - total_deductions

        payment = Payment(
            payment_type=payment_data.payment_type,
            payee_type=payment_data.payee_type,
            payee_id=payment_data.payee_id,
            payee_name=payment_data.payee_name,
            payee_email=payment_data.payee_email,
            gross_amount=payment_data.gross_amount,
            tax_withholding=payment_data.tax_withholding,
            deductions=payment_data.deductions,
            net_amount=net_amount,
            currency=payment_data.currency,
            payment_method_id=payment_data.payment_method_id,
            status="pending",
            scheduled_date=payment_data.scheduled_date,
            placement_id=payment_data.placement_id,
            referral_bonus_id=payment_data.referral_bonus_id,
            invoice_id=payment_data.invoice_id,
            timesheet_id=payment_data.timesheet_id,
            notes=payment_data.notes,
            metadata_extra=payment_data.metadata_extra or {},
        )

        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)

        logger.info(f"Payment created: {payment.payment_type} - ${net_amount} for {payment.payee_name}")
        return payment

    async def get_payment_by_id(self, payment_id: int) -> Optional[Payment]:
        """Get payment by ID.

        Args:
            payment_id: Payment ID

        Returns:
            Payment or None
        """
        stmt = select(Payment).where(Payment.id == payment_id).options(selectinload(Payment.method))
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_payments(
        self,
        payment_type: Optional[str] = None,
        status: Optional[str] = None,
        payee_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[List[Payment], int]:
        """List payments with filters.

        Args:
            payment_type: Filter by payment type
            status: Filter by status
            payee_type: Filter by payee type
            start_date: Filter by created after
            end_date: Filter by created before
            limit: Result limit
            offset: Result offset

        Returns:
            Tuple of payments and total count
        """
        stmt = select(Payment)

        filters = []
        if payment_type:
            filters.append(Payment.payment_type == payment_type)
        if status:
            filters.append(Payment.status == status)
        if payee_type:
            filters.append(Payment.payee_type == payee_type)
        if start_date:
            filters.append(Payment.created_at >= start_date)
        if end_date:
            filters.append(Payment.created_at <= end_date)

        if filters:
            stmt = stmt.where(and_(*filters))

        count_stmt = stmt.select_entity_from(Payment)
        count_result = await self.db.execute(select(func.count()).select_from(count_stmt.subquery()))
        total = count_result.scalar()

        stmt = stmt.order_by(desc(Payment.created_at)).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        payments = result.scalars().all()

        return payments, total

    async def update_payment(self, payment_id: int, update_data: PaymentUpdate) -> Payment:
        """Update payment.

        Args:
            payment_id: Payment ID
            update_data: Update data

        Returns:
            Updated payment

        Raises:
            ValueError: If payment not found
        """
        payment = await self.get_payment_by_id(payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")

        if update_data.status and update_data.status != payment.status:
            # Validate status transition
            if payment.status == "completed":
                raise ValueError("Cannot change status of completed payment")

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(payment, key, value)

        await self.db.commit()
        await self.db.refresh(payment)

        logger.info(f"Payment {payment_id} updated")
        return payment

    async def cancel_payment(self, payment_id: int) -> Payment:
        """Cancel payment.

        Args:
            payment_id: Payment ID

        Returns:
            Cancelled payment

        Raises:
            ValueError: If payment cannot be cancelled
        """
        payment = await self.get_payment_by_id(payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")

        if payment.status not in ["pending", "processing"]:
            raise ValueError(f"Cannot cancel payment with status {payment.status}")

        payment.status = "cancelled"
        await self.db.commit()
        await self.db.refresh(payment)

        logger.info(f"Payment {payment_id} cancelled")
        return payment

    # Payment methods

    async def add_payment_method(self, method_data: PaymentMethodCreate) -> PaymentMethod:
        """Add payment method.

        Args:
            method_data: Payment method data

        Returns:
            Created payment method

        Raises:
            ValueError: If validation fails
        """
        # Check if default method exists
        if method_data.is_default:
            existing_default = await self._get_default_method(
                method_data.entity_type, method_data.entity_id
            )
            if existing_default:
                existing_default.is_default = False
                self.db.add(existing_default)

        method = PaymentMethod(
            entity_type=method_data.entity_type,
            entity_id=method_data.entity_id,
            method_type=method_data.method_type,
            gateway=method_data.gateway,
            last_four=method_data.last_four,
            bank_name=method_data.bank_name,
            account_holder_name=method_data.account_holder_name,
            routing_number_last_four=method_data.routing_number_last_four,
            paypal_email=method_data.paypal_email,
            is_default=method_data.is_default,
            is_verified=False,
        )

        self.db.add(method)
        await self.db.commit()
        await self.db.refresh(method)

        logger.info(f"Payment method added for {method_data.entity_type} {method_data.entity_id}")
        return method

    async def get_payment_method_by_id(self, method_id: int) -> Optional[PaymentMethod]:
        """Get payment method by ID.

        Args:
            method_id: Method ID

        Returns:
            Payment method or None
        """
        stmt = select(PaymentMethod).where(PaymentMethod.id == method_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_payment_methods(self, entity_type: str, entity_id: int) -> List[PaymentMethod]:
        """Get payment methods for entity.

        Args:
            entity_type: Entity type
            entity_id: Entity ID

        Returns:
            List of payment methods
        """
        stmt = (
            select(PaymentMethod)
            .where(and_(PaymentMethod.entity_type == entity_type, PaymentMethod.entity_id == entity_id))
            .order_by(PaymentMethod.is_default.desc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def delete_payment_method(self, method_id: int) -> None:
        """Delete payment method.

        Args:
            method_id: Method ID

        Raises:
            ValueError: If method not found
        """
        method = await self.get_payment_method_by_id(method_id)
        if not method:
            raise ValueError(f"Payment method {method_id} not found")

        await self.db.delete(method)
        await self.db.commit()

        logger.info(f"Payment method {method_id} deleted")

    # Payment schedules

    async def create_schedule(self, schedule_data: PaymentScheduleCreate) -> PaymentSchedule:
        """Create payment schedule.

        Args:
            schedule_data: Schedule creation data

        Returns:
            Created schedule

        Raises:
            ValueError: If validation fails
        """
        if not schedule_data.amount and not schedule_data.rate:
            raise ValueError("Either amount or rate must be provided")

        # Calculate next payment date
        next_date = self._calculate_next_payment_date(schedule_data.start_date, schedule_data.frequency)

        schedule = PaymentSchedule(
            payee_type=schedule_data.payee_type,
            payee_id=schedule_data.payee_id,
            placement_id=schedule_data.placement_id,
            frequency=schedule_data.frequency,
            amount=schedule_data.amount,
            rate=schedule_data.rate,
            rate_type=schedule_data.rate_type,
            payment_method_id=schedule_data.payment_method_id,
            next_payment_date=next_date,
            start_date=schedule_data.start_date,
            end_date=schedule_data.end_date,
            is_active=True,
            auto_process=schedule_data.auto_process,
            total_paid=0.0,
            payments_count=0,
        )

        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule)

        logger.info(f"Payment schedule created: {schedule_data.frequency} for payee {schedule_data.payee_id}")
        return schedule

    async def get_schedule_by_id(self, schedule_id: int) -> Optional[PaymentSchedule]:
        """Get schedule by ID.

        Args:
            schedule_id: Schedule ID

        Returns:
            Schedule or None
        """
        stmt = select(PaymentSchedule).where(PaymentSchedule.id == schedule_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_schedules(
        self,
        payee_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[List[PaymentSchedule], int]:
        """List payment schedules.

        Args:
            payee_type: Filter by payee type
            is_active: Filter by active status
            limit: Result limit
            offset: Result offset

        Returns:
            Tuple of schedules and total count
        """
        stmt = select(PaymentSchedule)

        filters = []
        if payee_type:
            filters.append(PaymentSchedule.payee_type == payee_type)
        if is_active is not None:
            filters.append(PaymentSchedule.is_active == is_active)

        if filters:
            stmt = stmt.where(and_(*filters))

        count_stmt = stmt.select_entity_from(PaymentSchedule)
        count_result = await self.db.execute(select(func.count()).select_from(count_stmt.subquery()))
        total = count_result.scalar()

        stmt = stmt.order_by(desc(PaymentSchedule.created_at)).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        schedules = result.scalars().all()

        return schedules, total

    async def update_schedule(self, schedule_id: int, update_data: PaymentScheduleUpdate) -> PaymentSchedule:
        """Update schedule.

        Args:
            schedule_id: Schedule ID
            update_data: Update data

        Returns:
            Updated schedule

        Raises:
            ValueError: If schedule not found
        """
        schedule = await self.get_schedule_by_id(schedule_id)
        if not schedule:
            raise ValueError(f"Schedule {schedule_id} not found")

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(schedule, key, value)

        await self.db.commit()
        await self.db.refresh(schedule)

        logger.info(f"Schedule {schedule_id} updated")
        return schedule

    async def get_due_schedules(self) -> List[PaymentSchedule]:
        """Get schedules due for payment.

        Returns:
            List of due schedules
        """
        today = date.today()
        stmt = select(PaymentSchedule).where(
            and_(
                PaymentSchedule.is_active == True,
                PaymentSchedule.next_payment_date <= today,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    # Reconciliation

    async def create_reconciliation(
        self, period_start: date, period_end: date
    ) -> PaymentReconciliation:
        """Create reconciliation record.

        Args:
            period_start: Period start date
            period_end: Period end date

        Returns:
            Created reconciliation

        Raises:
            ValueError: If dates are invalid
        """
        if period_start > period_end:
            raise ValueError("Start date must be before end date")

        # Get payments for period
        stmt = select(Payment).where(
            and_(
                Payment.created_at >= datetime.combine(period_start, datetime.min.time()),
                Payment.created_at <= datetime.combine(period_end, datetime.max.time()),
                Payment.status == "completed",
            )
        )
        result = await self.db.execute(stmt)
        payments = result.scalars().all()

        total_paid_out = sum(float(p.net_amount) for p in payments)

        reconciliation = PaymentReconciliation(
            period_start=period_start,
            period_end=period_end,
            total_paid_out=total_paid_out,
            status="pending",
            payment_count=len(payments),
        )

        self.db.add(reconciliation)
        await self.db.commit()
        await self.db.refresh(reconciliation)

        logger.info(f"Reconciliation created for {period_start} to {period_end}")
        return reconciliation

    async def get_reconciliation_by_id(self, reconciliation_id: int) -> Optional[PaymentReconciliation]:
        """Get reconciliation by ID.

        Args:
            reconciliation_id: Reconciliation ID

        Returns:
            Reconciliation or None
        """
        stmt = select(PaymentReconciliation).where(PaymentReconciliation.id == reconciliation_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_reconciliations(
        self, limit: int = 100, offset: int = 0
    ) -> tuple[List[PaymentReconciliation], int]:
        """List reconciliations.

        Args:
            limit: Result limit
            offset: Result offset

        Returns:
            Tuple of reconciliations and total count
        """
        stmt = select(PaymentReconciliation).order_by(desc(PaymentReconciliation.period_start))

        count_result = await self.db.execute(select(func.count(PaymentReconciliation.id)))
        total = count_result.scalar()

        stmt = stmt.limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        reconciliations = result.scalars().all()

        return reconciliations, total

    async def update_reconciliation(
        self, reconciliation_id: int, status: str, notes: Optional[str] = None, reconciled_by: Optional[int] = None
    ) -> PaymentReconciliation:
        """Update reconciliation status.

        Args:
            reconciliation_id: Reconciliation ID
            status: New status
            notes: Optional notes
            reconciled_by: User ID

        Returns:
            Updated reconciliation

        Raises:
            ValueError: If reconciliation not found
        """
        reconciliation = await self.get_reconciliation_by_id(reconciliation_id)
        if not reconciliation:
            raise ValueError(f"Reconciliation {reconciliation_id} not found")

        reconciliation.status = status
        reconciliation.notes = notes
        reconciliation.reconciled_by = reconciled_by
        if status == "resolved":
            reconciliation.reconciled_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(reconciliation)

        logger.info(f"Reconciliation {reconciliation_id} updated to {status}")
        return reconciliation

    # Analytics

    async def get_payment_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get payment analytics.

        Args:
            days: Days to analyze

        Returns:
            Analytics data
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        stmt = select(Payment).where(Payment.created_at >= cutoff_date)
        result = await self.db.execute(stmt)
        payments = result.scalars().all()

        total_processed = len([p for p in payments if p.status == "completed"])
        total_failed = len([p for p in payments if p.status == "failed"])
        total_amount = sum(float(p.net_amount) for p in payments if p.status == "completed")

        by_type = {}
        by_method = {}

        for payment in payments:
            by_type[payment.payment_type] = by_type.get(payment.payment_type, 0) + 1
            if payment.payment_method_type:
                by_method[payment.payment_method_type] = by_method.get(payment.payment_method_type, 0) + 1

        analytics = {
            "period_days": days,
            "total_payments": len(payments),
            "total_processed": total_processed,
            "total_failed": total_failed,
            "failure_rate": (total_failed / len(payments) * 100) if payments else 0,
            "total_amount": total_amount,
            "by_type": by_type,
            "by_method": by_method,
        }

        return analytics

    # Helper methods

    async def _get_default_method(self, entity_type: str, entity_id: int) -> Optional[PaymentMethod]:
        """Get default payment method for entity."""
        stmt = select(PaymentMethod).where(
            and_(
                PaymentMethod.entity_type == entity_type,
                PaymentMethod.entity_id == entity_id,
                PaymentMethod.is_default == True,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    def _calculate_next_payment_date(self, current_date: date, frequency: str) -> date:
        """Calculate next payment date."""
        if frequency == "weekly":
            return current_date + timedelta(days=7)
        elif frequency == "bi_weekly":
            return current_date + timedelta(days=14)
        elif frequency == "semi_monthly":
            return current_date + timedelta(days=15)
        else:  # monthly
            return current_date + timedelta(days=30)
