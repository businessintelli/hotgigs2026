"""Rate card management endpoints for VMS billing."""

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from api.dependencies import get_current_user, get_db, require_role, get_tenant_context_dep
from database.tenant_context import TenantContext
from models.user import User
from models.rate_card import RateCard, RateCardEntry
from schemas.rate_card import (
    RateCardCreate, RateCardUpdate, RateCardResponse, RateValidationRequest, RateValidationResponse
)
from services.rate_card_service import RateCardService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rate-cards", tags=["Rate Cards"])


@router.post("", response_model=RateCardResponse, status_code=status.HTTP_201_CREATED)
async def create_rate_card(
    data: RateCardCreate,
    user: User = Depends(require_role("client_admin", "msp_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """Create a new rate card with entries."""
    try:
        svc = RateCardService(db)
        rate_card = await svc.create_rate_card(data.model_dump())
        return RateCardResponse.model_validate(rate_card)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating rate card: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("", response_model=List[RateCardResponse])
async def list_rate_cards(
    client_org_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    user: User = Depends(require_role("client_admin", "msp_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """List rate cards with optional filtering."""
    try:
        svc = RateCardService(db)
        rate_cards = await svc.list_rate_cards(client_org_id=client_org_id, status=status_filter)
        return [RateCardResponse.model_validate(rc) for rc in rate_cards]
    except Exception as e:
        logger.error(f"Error listing rate cards: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{rate_card_id}", response_model=RateCardResponse)
async def get_rate_card(
    rate_card_id: int,
    user: User = Depends(require_role("client_admin", "msp_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """Get a rate card by ID with all entries."""
    try:
        result = await db.execute(select(RateCard).where(RateCard.id == rate_card_id))
        rate_card = result.scalar_one_or_none()
        if not rate_card:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rate card not found")
        return RateCardResponse.model_validate(rate_card)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching rate card: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/{rate_card_id}", response_model=RateCardResponse)
async def update_rate_card(
    rate_card_id: int,
    update_data: RateCardUpdate,
    user: User = Depends(require_role("client_admin", "msp_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """Update a rate card."""
    try:
        result = await db.execute(select(RateCard).where(RateCard.id == rate_card_id))
        rate_card = result.scalar_one_or_none()
        if not rate_card:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rate card not found")

        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(rate_card, key):
                setattr(rate_card, key, value)

        db.add(rate_card)
        await db.commit()
        await db.refresh(rate_card)
        return RateCardResponse.model_validate(rate_card)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating rate card: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/validate", response_model=RateValidationResponse)
async def validate_rates(
    request: RateValidationRequest,
    user: User = Depends(require_role("client_admin", "msp_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """Validate proposed rates against applicable rate card."""
    try:
        svc = RateCardService(db)
        is_valid, details = await svc.validate_submission_rates(
            client_org_id=request.client_org_id,
            job_category=request.job_category,
            bill_rate=request.bill_rate,
            pay_rate=request.pay_rate,
            location=request.location,
        )
        return RateValidationResponse(
            is_valid=is_valid,
            rate_card_id=details.get("rate_card_id"),
            violations=details.get("violations", []),
            message="Rates are valid" if is_valid else "Rates violate rate card constraints",
        )
    except Exception as e:
        logger.error(f"Error validating rates: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/{rate_card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_rate_card(
    rate_card_id: int,
    user: User = Depends(require_role("msp_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a rate card by archiving it."""
    try:
        result = await db.execute(select(RateCard).where(RateCard.id == rate_card_id))
        rate_card = result.scalar_one_or_none()
        if not rate_card:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rate card not found")

        rate_card.status = "ARCHIVED"
        db.add(rate_card)
        await db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error archiving rate card: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
