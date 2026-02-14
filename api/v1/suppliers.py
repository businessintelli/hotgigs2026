"""Supplier network management API endpoints."""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from schemas.supplier import (
    SupplierCreate,
    SupplierUpdate,
    SupplierResponse,
    SupplierPerformanceResponse,
)
from schemas.supplier_network import (
    SupplierRequirementResponse,
    SupplierRateCardCreate,
    SupplierRateCardResponse,
    SupplierCommunicationResponse,
)
from schemas.common import PaginatedResponse
from services.supplier_service import SupplierService
from agents.supplier_network_agent import SupplierNetworkAgent
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/suppliers", tags=["suppliers"])

# Initialize agent
supplier_agent = SupplierNetworkAgent(anthropic_api_key=settings.anthropic_api_key)


@router.post("", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    supplier_data: SupplierCreate,
    db: AsyncSession = Depends(get_db),
) -> SupplierResponse:
    """Create a new supplier.

    Args:
        supplier_data: Supplier creation data
        db: Database session

    Returns:
        Created supplier
    """
    try:
        supplier = await supplier_agent.onboard_supplier(db, supplier_data.model_dump())
        return SupplierResponse.model_validate(supplier)
    except Exception as e:
        logger.error(f"Error creating supplier: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=PaginatedResponse[SupplierResponse])
async def list_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    tier: Optional[str] = None,
    specialization: Optional[str] = None,
    location: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[SupplierResponse]:
    """List suppliers with optional filters.

    Args:
        skip: Number to skip
        limit: Number to limit
        tier: Filter by tier
        specialization: Filter by specialization
        location: Filter by location
        db: Database session

    Returns:
        Paginated supplier list
    """
    try:
        suppliers, total = await SupplierService.list_suppliers(
            db,
            skip=skip,
            limit=limit,
            tier=tier,
            specialization=specialization,
            location=location,
        )

        items = [SupplierResponse.model_validate(s) for s in suppliers]
        return PaginatedResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=items,
        )
    except Exception as e:
        logger.error(f"Error listing suppliers: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: int,
    db: AsyncSession = Depends(get_db),
) -> SupplierResponse:
    """Get supplier details.

    Args:
        supplier_id: Supplier ID
        db: Database session

    Returns:
        Supplier details
    """
    try:
        supplier = await SupplierService.get_supplier(db, supplier_id)
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")

        return SupplierResponse.model_validate(supplier)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting supplier: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: int,
    supplier_data: SupplierUpdate,
    db: AsyncSession = Depends(get_db),
) -> SupplierResponse:
    """Update supplier.

    Args:
        supplier_id: Supplier ID
        supplier_data: Update data
        db: Database session

    Returns:
        Updated supplier
    """
    try:
        supplier = await SupplierService.update_supplier(
            db, supplier_id, **supplier_data.model_dump(exclude_unset=True)
        )
        return SupplierResponse.model_validate(supplier)
    except Exception as e:
        logger.error(f"Error updating supplier: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{supplier_id}/distribute", response_model=List[SupplierRequirementResponse])
async def distribute_requirement_to_supplier(
    supplier_id: int,
    requirement_id: int,
    db: AsyncSession = Depends(get_db),
) -> List[SupplierRequirementResponse]:
    """Distribute requirement to supplier.

    Args:
        supplier_id: Supplier ID
        requirement_id: Requirement ID
        db: Database session

    Returns:
        Distribution record
    """
    try:
        distributions = await supplier_agent.distribute_requirement(
            db, requirement_id, supplier_ids=[supplier_id]
        )

        return [
            SupplierRequirementResponse.model_validate(d) for d in distributions
        ]
    except Exception as e:
        logger.error(f"Error distributing requirement: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/distribute-requirement/{requirement_id}",
    response_model=List[SupplierRequirementResponse],
)
async def distribute_to_multiple(
    requirement_id: int,
    supplier_ids: Optional[List[int]] = None,
    auto_select: bool = False,
    db: AsyncSession = Depends(get_db),
) -> List[SupplierRequirementResponse]:
    """Distribute requirement to multiple suppliers or auto-select.

    Args:
        requirement_id: Requirement ID
        supplier_ids: List of supplier IDs
        auto_select: Whether to auto-select
        db: Database session

    Returns:
        Distribution records
    """
    try:
        distributions = await supplier_agent.distribute_requirement(
            db, requirement_id, supplier_ids=supplier_ids, auto_select=auto_select
        )

        return [
            SupplierRequirementResponse.model_validate(d) for d in distributions
        ]
    except Exception as e:
        logger.error(f"Error distributing requirement: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{supplier_id}/performance", response_model=List[SupplierPerformanceResponse])
async def get_supplier_performance(
    supplier_id: int,
    days: int = Query(180, ge=1),
    db: AsyncSession = Depends(get_db),
) -> List[SupplierPerformanceResponse]:
    """Get supplier performance history.

    Args:
        supplier_id: Supplier ID
        days: Days to look back
        db: Database session

    Returns:
        Performance history
    """
    try:
        performances = await SupplierService.get_supplier_performance(
            db, supplier_id, days=days
        )

        return [
            SupplierPerformanceResponse.model_validate(p) for p in performances
        ]
    except Exception as e:
        logger.error(f"Error getting performance: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{supplier_id}/evaluate", response_model=SupplierPerformanceResponse)
async def evaluate_supplier_performance(
    supplier_id: int,
    db: AsyncSession = Depends(get_db),
) -> SupplierPerformanceResponse:
    """Trigger performance evaluation for supplier.

    Args:
        supplier_id: Supplier ID
        db: Database session

    Returns:
        Performance evaluation result
    """
    try:
        from datetime import datetime, timedelta

        now = datetime.utcnow()
        period_start = (now - timedelta(days=30)).date()
        period_end = now.date()

        performance = await supplier_agent.evaluate_performance(
            db, supplier_id, period_start, period_end
        )

        return SupplierPerformanceResponse.model_validate(performance)
    except Exception as e:
        logger.error(f"Error evaluating performance: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{supplier_id}/scorecard")
async def get_supplier_scorecard(
    supplier_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get comprehensive supplier scorecard.

    Args:
        supplier_id: Supplier ID
        db: Database session

    Returns:
        Supplier scorecard
    """
    try:
        scorecard = await supplier_agent.generate_supplier_scorecard(db, supplier_id)
        return scorecard
    except Exception as e:
        logger.error(f"Error getting scorecard: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{supplier_id}/rate-card", response_model=SupplierRateCardResponse)
async def update_rate_card(
    supplier_id: int,
    rate_card: SupplierRateCardCreate,
    db: AsyncSession = Depends(get_db),
) -> SupplierRateCardResponse:
    """Update supplier rate card.

    Args:
        supplier_id: Supplier ID
        rate_card: Rate card data
        db: Database session

    Returns:
        Updated rate card
    """
    try:
        rate_card_data = await supplier_agent.manage_rate_cards(
            db, supplier_id, rate_card.model_dump()
        )

        return SupplierRateCardResponse.model_validate(rate_card_data)
    except Exception as e:
        logger.error(f"Error updating rate card: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{supplier_id}/communications", response_model=List[SupplierCommunicationResponse])
async def get_communications(
    supplier_id: int,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> List[SupplierCommunicationResponse]:
    """Get supplier communication history.

    Args:
        supplier_id: Supplier ID
        limit: Number to return
        db: Database session

    Returns:
        Communication records
    """
    try:
        communications = await SupplierService.get_communications(
            db, supplier_id, limit=limit
        )

        return [
            SupplierCommunicationResponse.model_validate(c) for c in communications
        ]
    except Exception as e:
        logger.error(f"Error getting communications: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/analytics/network")
async def get_network_analytics(
    db: AsyncSession = Depends(get_db),
):
    """Get network-wide analytics.

    Args:
        db: Database session

    Returns:
        Network analytics
    """
    try:
        analytics = await supplier_agent.get_network_analytics(db)
        return analytics
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/discover")
async def discover_suppliers(
    industry: Optional[str] = None,
    skills: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Discover supplier gaps and recommendations.

    Args:
        industry: Industry filter
        skills: Skills (comma-separated)
        db: Database session

    Returns:
        Supplier recommendations
    """
    try:
        skills_list = skills.split(",") if skills else None

        recommendations = await supplier_agent.discover_suppliers(
            db, industry=industry, skills=skills_list
        )

        return {"recommendations": recommendations}
    except Exception as e:
        logger.error(f"Error discovering suppliers: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
