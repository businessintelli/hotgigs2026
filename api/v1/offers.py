"""Offer and onboarding API endpoints."""

import logging
import json
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from schemas.offer import (
    OfferCreate,
    OfferUpdate,
    OfferResponse,
    OnboardingCreate,
    OnboardingUpdate,
    OnboardingResponse,
    ChecklistItemModel,
)
from schemas.common import PaginatedResponse
from services.offer_service import OfferService, OnboardingService
from agents.offer_onboarding_agent import OfferOnboardingAgent
from models.enums import OfferStatus, OnboardingStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/offers", tags=["offers", "onboarding"])
workflow_agent = OfferOnboardingAgent()


# ===== OFFER ENDPOINTS =====


@router.post("", response_model=OfferResponse, status_code=status.HTTP_201_CREATED)
async def create_offer(
    offer_data: OfferCreate,
    db: AsyncSession = Depends(get_db),
) -> OfferResponse:
    """Create a new offer.

    Args:
        offer_data: Offer creation data
        db: Database session

    Returns:
        Created offer
    """
    try:
        service = OfferService(db)
        offer = await service.create_offer(offer_data)
        return OfferResponse.from_orm(offer)
    except Exception as e:
        logger.error(f"Error creating offer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create offer",
        )


@router.get("/{offer_id}", response_model=OfferResponse)
async def get_offer(
    offer_id: int,
    db: AsyncSession = Depends(get_db),
) -> OfferResponse:
    """Get offer by ID.

    Args:
        offer_id: Offer ID
        db: Database session

    Returns:
        Offer data
    """
    try:
        service = OfferService(db)
        offer = await service.get_offer(offer_id)
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offer not found",
            )
        return OfferResponse.from_orm(offer)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting offer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get offer",
        )


@router.get("", response_model=PaginatedResponse[OfferResponse])
async def list_offers(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    candidate_id: Optional[int] = None,
    requirement_id: Optional[int] = None,
    status: Optional[OfferStatus] = None,
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[OfferResponse]:
    """List offers with filtering and pagination.

    Args:
        skip: Skip count
        limit: Result limit
        candidate_id: Filter by candidate
        requirement_id: Filter by requirement
        status: Filter by status
        db: Database session

    Returns:
        Paginated offers
    """
    try:
        service = OfferService(db)
        offers, total = await service.get_offers(
            skip=skip,
            limit=limit,
            candidate_id=candidate_id,
            requirement_id=requirement_id,
            status=status,
        )
        return PaginatedResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=[OfferResponse.from_orm(o) for o in offers],
        )
    except Exception as e:
        logger.error(f"Error listing offers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list offers",
        )


@router.put("/{offer_id}", response_model=OfferResponse)
async def update_offer(
    offer_id: int,
    offer_data: OfferUpdate,
    db: AsyncSession = Depends(get_db),
) -> OfferResponse:
    """Update offer.

    Args:
        offer_id: Offer ID
        offer_data: Update data
        db: Database session

    Returns:
        Updated offer
    """
    try:
        service = OfferService(db)
        offer = await service.update_offer(offer_id, offer_data)
        return OfferResponse.from_orm(offer)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error updating offer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update offer",
        )


@router.delete("/{offer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_offer(
    offer_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft delete offer.

    Args:
        offer_id: Offer ID
        db: Database session
    """
    try:
        service = OfferService(db)
        await service.delete_offer(offer_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error deleting offer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete offer",
        )


@router.post("/{offer_id}/send", response_model=OfferResponse)
async def send_offer(
    offer_id: int,
    db: AsyncSession = Depends(get_db),
) -> OfferResponse:
    """Send offer to candidate.

    Args:
        offer_id: Offer ID
        db: Database session

    Returns:
        Updated offer
    """
    try:
        offer = await workflow_agent.send_offer(db, offer_id)
        return OfferResponse.from_orm(offer)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error sending offer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send offer",
        )


@router.post("/{offer_id}/accept", response_model=OfferResponse)
async def accept_offer(
    offer_id: int,
    notes: str = Query(""),
    db: AsyncSession = Depends(get_db),
) -> OfferResponse:
    """Accept offer.

    Args:
        offer_id: Offer ID
        notes: Optional candidate notes
        db: Database session

    Returns:
        Updated offer
    """
    try:
        offer = await workflow_agent.process_response(db, offer_id, True, notes)
        return OfferResponse.from_orm(offer)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error accepting offer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to accept offer",
        )


@router.post("/{offer_id}/decline", response_model=OfferResponse)
async def decline_offer(
    offer_id: int,
    notes: str = Query(""),
    db: AsyncSession = Depends(get_db),
) -> OfferResponse:
    """Decline offer.

    Args:
        offer_id: Offer ID
        notes: Optional candidate notes
        db: Database session

    Returns:
        Updated offer
    """
    try:
        offer = await workflow_agent.process_response(db, offer_id, False, notes)
        return OfferResponse.from_orm(offer)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error declining offer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to decline offer",
        )


@router.post("/{offer_id}/negotiate", response_model=OfferResponse)
async def negotiate_offer(
    offer_id: int,
    counter_rate: float = Query(..., gt=0),
    counter_terms: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> OfferResponse:
    """Handle offer negotiation.

    Args:
        offer_id: Offer ID
        counter_rate: Counter offer rate
        counter_terms: Counter offer terms (JSON string)
        db: Database session

    Returns:
        Updated offer
    """
    try:
        counter_terms_dict = json.loads(counter_terms) if counter_terms else {}
        offer = await workflow_agent.handle_negotiation(
            db, offer_id, counter_rate, counter_terms_dict
        )
        return OfferResponse.from_orm(offer)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error negotiating offer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to negotiate offer",
        )


@router.get("/analytics")
async def get_offer_analytics(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get offer analytics.

    Args:
        db: Database session

    Returns:
        Analytics data
    """
    try:
        analytics = await workflow_agent.get_offer_analytics(db)
        return analytics
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get analytics",
        )


# ===== ONBOARDING ENDPOINTS =====


@router.post("/onboarding", response_model=OnboardingResponse, status_code=status.HTTP_201_CREATED)
async def create_onboarding(
    offer_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
) -> OnboardingResponse:
    """Start onboarding process.

    Args:
        offer_id: Offer ID
        db: Database session

    Returns:
        Created onboarding
    """
    try:
        onboarding = await workflow_agent.start_onboarding(db, offer_id)
        return OnboardingResponse.from_orm(onboarding)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error starting onboarding: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start onboarding",
        )


@router.get("/onboarding/{onboarding_id}", response_model=OnboardingResponse)
async def get_onboarding(
    onboarding_id: int,
    db: AsyncSession = Depends(get_db),
) -> OnboardingResponse:
    """Get onboarding by ID.

    Args:
        onboarding_id: Onboarding ID
        db: Database session

    Returns:
        Onboarding data
    """
    try:
        service = OnboardingService(db)
        onboarding = await service.get_onboarding(onboarding_id)
        if not onboarding:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Onboarding not found",
            )
        return OnboardingResponse.from_orm(onboarding)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting onboarding: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get onboarding",
        )


@router.get("/onboarding", response_model=PaginatedResponse[OnboardingResponse])
async def list_onboardings(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    candidate_id: Optional[int] = None,
    status: Optional[OnboardingStatus] = None,
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[OnboardingResponse]:
    """List onboardings with filtering and pagination.

    Args:
        skip: Skip count
        limit: Result limit
        candidate_id: Filter by candidate
        status: Filter by status
        db: Database session

    Returns:
        Paginated onboardings
    """
    try:
        service = OnboardingService(db)
        onboardings, total = await service.get_onboardings(
            skip=skip,
            limit=limit,
            candidate_id=candidate_id,
            status=status,
        )
        return PaginatedResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=[OnboardingResponse.from_orm(o) for o in onboardings],
        )
    except Exception as e:
        logger.error(f"Error listing onboardings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list onboardings",
        )


@router.put("/onboarding/{onboarding_id}", response_model=OnboardingResponse)
async def update_onboarding(
    onboarding_id: int,
    onboarding_data: OnboardingUpdate,
    db: AsyncSession = Depends(get_db),
) -> OnboardingResponse:
    """Update onboarding.

    Args:
        onboarding_id: Onboarding ID
        onboarding_data: Update data
        db: Database session

    Returns:
        Updated onboarding
    """
    try:
        service = OnboardingService(db)
        onboarding = await service.update_onboarding(
            onboarding_id, onboarding_data
        )
        return OnboardingResponse.from_orm(onboarding)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error updating onboarding: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update onboarding",
        )


@router.post("/onboarding/{onboarding_id}/checklist/{item_name}")
async def update_checklist_item(
    onboarding_id: int,
    item_name: str,
    completed: bool = Query(...),
    db: AsyncSession = Depends(get_db),
) -> OnboardingResponse:
    """Update checklist item status.

    Args:
        onboarding_id: Onboarding ID
        item_name: Checklist item name
        completed: Whether item is completed
        db: Database session

    Returns:
        Updated onboarding
    """
    try:
        onboarding = await workflow_agent.update_checklist_item(
            db, onboarding_id, item_name, completed
        )
        return OnboardingResponse.from_orm(onboarding)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error updating checklist: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update checklist",
        )


@router.post("/onboarding/{onboarding_id}/complete", response_model=OnboardingResponse)
async def complete_onboarding(
    onboarding_id: int,
    db: AsyncSession = Depends(get_db),
) -> OnboardingResponse:
    """Complete onboarding process.

    Args:
        onboarding_id: Onboarding ID
        db: Database session

    Returns:
        Updated onboarding
    """
    try:
        onboarding = await workflow_agent.complete_onboarding(db, onboarding_id)
        return OnboardingResponse.from_orm(onboarding)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error completing onboarding: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete onboarding",
        )


@router.post("/onboarding/{onboarding_id}/backout", response_model=OnboardingResponse)
async def handle_backout(
    onboarding_id: int,
    reason: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> OnboardingResponse:
    """Handle candidate backout.

    Args:
        onboarding_id: Onboarding ID
        reason: Backout reason
        db: Database session

    Returns:
        Updated onboarding
    """
    try:
        onboarding = await workflow_agent.handle_backout(db, onboarding_id, reason)
        return OnboardingResponse.from_orm(onboarding)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error handling backout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to handle backout",
        )


@router.get("/onboarding/{onboarding_id}/progress")
async def get_onboarding_progress(
    onboarding_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get onboarding progress.

    Args:
        onboarding_id: Onboarding ID
        db: Database session

    Returns:
        Progress data
    """
    try:
        service = OnboardingService(db)
        progress = await service.get_onboarding_progress(onboarding_id)
        return progress
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error getting progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get progress",
        )
