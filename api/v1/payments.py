"""Payment processing API endpoints."""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime

from api.dependencies import get_db
from schemas.payment import (
    PaymentCreate,
    PaymentUpdate,
    PaymentResponse,
    PaymentMethodCreate,
    PaymentMethodResponse,
    PaymentScheduleCreate,
    PaymentScheduleUpdate,
    PaymentScheduleResponse,
    PaymentReconciliationCreate,
    PaymentReconciliationResponse,
    PaymentBatchProcess,
    PaymentBatchResult,
    PaymentReport,
    PaymentAnalytics,
    TaxDocumentation,
    ReferralBonusPayoutResponse,
    SupplierCommissionResponse,
)
from schemas.common import BaseResponse
from services.payment_service import PaymentService
from agents.payment_processing_agent import PaymentProcessingAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])
agent = PaymentProcessingAgent()


# Payment endpoints

@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    user_id: Optional[int] = None,
) -> PaymentResponse:
    """Create payment.

    Args:
        payment_data: Payment creation data
        db: Database session
        user_id: User ID

    Returns:
        Created payment
    """
    try:
        service = PaymentService(db)
        payment = await service.create_payment(payment_data)
        return PaymentResponse.from_orm(payment)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment",
        )


@router.get("", response_model=dict)
async def list_payments(
    payment_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    payee_type: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List payments.

    Args:
        payment_type: Filter by type
        status: Filter by status
        payee_type: Filter by payee type
        start_date: Filter by start date
        end_date: Filter by end date
        limit: Result limit
        offset: Result offset
        db: Database session

    Returns:
        List of payments with count
    """
    try:
        service = PaymentService(db)
        payments, total = await service.list_payments(
            payment_type=payment_type,
            status=status,
            payee_type=payee_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )
        return {
            "data": [PaymentResponse.from_orm(p) for p in payments],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        logger.error(f"Error listing payments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list payments",
        )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
) -> PaymentResponse:
    """Get payment by ID.

    Args:
        payment_id: Payment ID
        db: Database session

    Returns:
        Payment details
    """
    try:
        service = PaymentService(db)
        payment = await service.get_payment_by_id(payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found",
            )
        return PaymentResponse.from_orm(payment)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get payment",
        )


@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: int,
    update_data: PaymentUpdate,
    db: AsyncSession = Depends(get_db),
) -> PaymentResponse:
    """Update payment.

    Args:
        payment_id: Payment ID
        update_data: Update data
        db: Database session

    Returns:
        Updated payment
    """
    try:
        service = PaymentService(db)
        payment = await service.update_payment(payment_id, update_data)
        return PaymentResponse.from_orm(payment)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update payment",
        )


@router.post("/{payment_id}/process", response_model=dict)
async def process_payment(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Process payment.

    Args:
        payment_id: Payment ID
        db: Database session

    Returns:
        Processing result
    """
    try:
        result = await agent.process_payment(db, payment_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process payment",
        )


@router.post("/batch-process", response_model=PaymentBatchResult)
async def batch_process_payments(
    batch_data: PaymentBatchProcess,
    db: AsyncSession = Depends(get_db),
) -> PaymentBatchResult:
    """Process multiple payments in batch.

    Args:
        batch_data: Batch data with payment IDs
        db: Database session

    Returns:
        Batch processing result
    """
    try:
        result = await agent.process_batch_payments(db, batch_data.payment_ids)
        return PaymentBatchResult(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process batch",
        )


@router.post("/{payment_id}/cancel", response_model=PaymentResponse)
async def cancel_payment(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
) -> PaymentResponse:
    """Cancel payment.

    Args:
        payment_id: Payment ID
        db: Database session

    Returns:
        Cancelled payment
    """
    try:
        service = PaymentService(db)
        payment = await service.cancel_payment(payment_id)
        return PaymentResponse.from_orm(payment)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error cancelling payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel payment",
        )


# Payment method endpoints

@router.post("/methods", response_model=PaymentMethodResponse, status_code=status.HTTP_201_CREATED)
async def add_payment_method(
    method_data: PaymentMethodCreate,
    db: AsyncSession = Depends(get_db),
) -> PaymentMethodResponse:
    """Add payment method.

    Args:
        method_data: Payment method data
        db: Database session

    Returns:
        Created payment method
    """
    try:
        service = PaymentService(db)
        method = await service.add_payment_method(method_data)
        return PaymentMethodResponse.from_orm(method)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding payment method: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add payment method",
        )


@router.get("/methods/{entity_type}/{entity_id}", response_model=List[PaymentMethodResponse])
async def get_payment_methods(
    entity_type: str,
    entity_id: int,
    db: AsyncSession = Depends(get_db),
) -> List[PaymentMethodResponse]:
    """Get payment methods for entity.

    Args:
        entity_type: Entity type
        entity_id: Entity ID
        db: Database session

    Returns:
        List of payment methods
    """
    try:
        service = PaymentService(db)
        methods = await service.get_payment_methods(entity_type, entity_id)
        return [PaymentMethodResponse.from_orm(m) for m in methods]
    except Exception as e:
        logger.error(f"Error getting payment methods: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get payment methods",
        )


@router.delete("/methods/{method_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment_method(
    method_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete payment method.

    Args:
        method_id: Method ID
        db: Database session
    """
    try:
        service = PaymentService(db)
        await service.delete_payment_method(method_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting payment method: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete payment method",
        )


# Payment schedule endpoints

@router.post("/schedules", response_model=PaymentScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule_data: PaymentScheduleCreate,
    db: AsyncSession = Depends(get_db),
    user_id: Optional[int] = None,
) -> PaymentScheduleResponse:
    """Create payment schedule.

    Args:
        schedule_data: Schedule creation data
        db: Database session
        user_id: User ID

    Returns:
        Created schedule
    """
    try:
        service = PaymentService(db)
        schedule = await service.create_schedule(schedule_data)
        return PaymentScheduleResponse.from_orm(schedule)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating schedule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create schedule",
        )


@router.get("/schedules", response_model=dict)
async def list_schedules(
    payee_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List payment schedules.

    Args:
        payee_type: Filter by payee type
        is_active: Filter by active status
        limit: Result limit
        offset: Result offset
        db: Database session

    Returns:
        List of schedules with count
    """
    try:
        service = PaymentService(db)
        schedules, total = await service.list_schedules(
            payee_type=payee_type,
            is_active=is_active,
            limit=limit,
            offset=offset,
        )
        return {
            "data": [PaymentScheduleResponse.from_orm(s) for s in schedules],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        logger.error(f"Error listing schedules: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list schedules",
        )


@router.put("/schedules/{schedule_id}", response_model=PaymentScheduleResponse)
async def update_schedule(
    schedule_id: int,
    update_data: PaymentScheduleUpdate,
    db: AsyncSession = Depends(get_db),
) -> PaymentScheduleResponse:
    """Update schedule.

    Args:
        schedule_id: Schedule ID
        update_data: Update data
        db: Database session

    Returns:
        Updated schedule
    """
    try:
        service = PaymentService(db)
        schedule = await service.update_schedule(schedule_id, update_data)
        return PaymentScheduleResponse.from_orm(schedule)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating schedule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update schedule",
        )


@router.post("/schedules/process-due", response_model=dict)
async def process_due_schedules(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Process scheduled payments that are due.

    Args:
        db: Database session

    Returns:
        Processing result
    """
    try:
        result = await agent.process_scheduled_payments(db)
        return result
    except Exception as e:
        logger.error(f"Error processing scheduled payments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process scheduled payments",
        )


# Reconciliation endpoints

@router.post("/reconciliation", response_model=PaymentReconciliationResponse, status_code=status.HTTP_201_CREATED)
async def create_reconciliation(
    reconciliation_data: PaymentReconciliationCreate,
    db: AsyncSession = Depends(get_db),
    user_id: Optional[int] = None,
) -> PaymentReconciliationResponse:
    """Create reconciliation.

    Args:
        reconciliation_data: Reconciliation data
        db: Database session
        user_id: User ID

    Returns:
        Created reconciliation
    """
    try:
        service = PaymentService(db)
        reconciliation = await service.create_reconciliation(
            reconciliation_data.period_start,
            reconciliation_data.period_end,
        )
        return PaymentReconciliationResponse.from_orm(reconciliation)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating reconciliation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create reconciliation",
        )


@router.get("/reconciliation", response_model=dict)
async def list_reconciliations(
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List reconciliations.

    Args:
        limit: Result limit
        offset: Result offset
        db: Database session

    Returns:
        List of reconciliations with count
    """
    try:
        service = PaymentService(db)
        reconciliations, total = await service.list_reconciliations(limit=limit, offset=offset)
        return {
            "data": [PaymentReconciliationResponse.from_orm(r) for r in reconciliations],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        logger.error(f"Error listing reconciliations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list reconciliations",
        )


# Bonus & Commission endpoints

@router.post("/referral-bonus/{bonus_id}/payout", response_model=ReferralBonusPayoutResponse)
async def process_referral_bonus(
    bonus_id: int,
    db: AsyncSession = Depends(get_db),
) -> ReferralBonusPayoutResponse:
    """Process referral bonus payout.

    Args:
        bonus_id: Bonus ID
        db: Database session

    Returns:
        Payout result
    """
    try:
        result = await agent.process_referral_bonus_payout(db, bonus_id)
        return ReferralBonusPayoutResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing referral bonus: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process bonus",
        )


@router.post("/supplier-commission/{placement_id}", response_model=SupplierCommissionResponse)
async def process_supplier_commission(
    placement_id: int,
    db: AsyncSession = Depends(get_db),
) -> SupplierCommissionResponse:
    """Process supplier commission.

    Args:
        placement_id: Placement ID
        db: Database session

    Returns:
        Commission processing result
    """
    try:
        result = await agent.process_supplier_commission(db, placement_id)
        return SupplierCommissionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing supplier commission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process commission",
        )


# Analytics endpoints

@router.get("/report", response_model=PaymentReport)
async def get_payment_report(
    start_date: date,
    end_date: date,
    db: AsyncSession = Depends(get_db),
) -> PaymentReport:
    """Get payment report for period.

    Args:
        start_date: Period start date
        end_date: Period end date
        db: Database session

    Returns:
        Payment report
    """
    try:
        result = await agent.generate_payment_report(db, start_date, end_date)
        return PaymentReport(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating payment report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate report",
        )


@router.get("/analytics", response_model=PaymentAnalytics)
async def get_payment_analytics(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
) -> PaymentAnalytics:
    """Get payment analytics.

    Args:
        days: Days to analyze
        db: Database session

    Returns:
        Analytics data
    """
    try:
        result = await agent.get_payment_analytics(db)
        return PaymentAnalytics(**result)
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get analytics",
        )


@router.get("/1099/{tax_year}", response_model=List[TaxDocumentation])
async def get_1099_data(
    tax_year: int,
    db: AsyncSession = Depends(get_db),
) -> List[TaxDocumentation]:
    """Get 1099 tax data for year.

    Args:
        tax_year: Tax year
        db: Database session

    Returns:
        List of 1099 records
    """
    try:
        result = await agent.generate_1099_data(db, tax_year)
        return [TaxDocumentation(**r) for r in result]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating 1099 data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate 1099 data",
        )
