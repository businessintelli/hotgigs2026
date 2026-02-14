"""Digital marketing API endpoints."""

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db
from schemas.marketing import (
    MarketingCampaignCreate,
    MarketingCampaignUpdate,
    MarketingCampaignResponse,
    HotlistCreate,
    HotlistUpdate,
    HotlistResponse,
    CampaignDistributionResponse,
    GenerateJobAdRequest,
    GenerateJobAdResponse,
    GenerateBenchProfileRequest,
    GenerateBenchProfileResponse,
    GenerateSocialPostRequest,
    GenerateSocialPostResponse,
    CampaignPerformanceResponse,
    MarketingAnalyticsResponse,
)
from schemas.common import PaginatedResponse
from services.marketing_service import MarketingService
from agents.digital_marketing_agent import DigitalMarketingAgent
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/marketing", tags=["marketing"])
marketing_agent = DigitalMarketingAgent(anthropic_api_key=settings.anthropic_api_key)


# ===== MARKETING CAMPAIGN ENDPOINTS =====


@router.post("/campaigns", response_model=MarketingCampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: MarketingCampaignCreate,
    db: AsyncSession = Depends(get_db),
) -> MarketingCampaignResponse:
    """Create marketing campaign."""
    try:
        campaign = await marketing_agent.create_campaign(db, campaign_data.model_dump())
        await db.commit()
        return campaign

    except Exception as e:
        logger.error(f"Error creating campaign: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/campaigns", response_model=PaginatedResponse[MarketingCampaignResponse])
async def list_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[MarketingCampaignResponse]:
    """List marketing campaigns."""
    try:
        service = MarketingService(db)
        campaigns, total = await service.get_campaigns(skip=skip, limit=limit)

        # Filter by status if provided
        if status:
            campaigns = [c for c in campaigns if c.status == status]
            total = len(campaigns)

        return PaginatedResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=campaigns,
        )

    except Exception as e:
        logger.error(f"Error listing campaigns: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/campaigns/{campaign_id}", response_model=MarketingCampaignResponse)
async def get_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
) -> MarketingCampaignResponse:
    """Get campaign details."""
    try:
        service = MarketingService(db)
        campaign = await service.get_campaign_by_id(campaign_id)

        if not campaign:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

        return campaign

    except Exception as e:
        logger.error(f"Error getting campaign: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/campaigns/{campaign_id}", response_model=MarketingCampaignResponse)
async def update_campaign(
    campaign_id: int,
    campaign_update: MarketingCampaignUpdate,
    db: AsyncSession = Depends(get_db),
) -> MarketingCampaignResponse:
    """Update marketing campaign."""
    try:
        service = MarketingService(db)
        campaign = await service.update_campaign(campaign_id, campaign_update.model_dump(exclude_unset=True))

        if not campaign:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

        await db.commit()
        return campaign

    except Exception as e:
        logger.error(f"Error updating campaign: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/campaigns/{campaign_id}/distribute")
async def distribute_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Distribute campaign across channels."""
    try:
        results = await marketing_agent.distribute_campaign(db, campaign_id)
        await db.commit()

        return {
            "campaign_id": campaign_id,
            "distributions": results,
        }

    except Exception as e:
        logger.error(f"Error distributing campaign: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/campaigns/{campaign_id}/pause", response_model=MarketingCampaignResponse)
async def pause_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
) -> MarketingCampaignResponse:
    """Pause a marketing campaign."""
    try:
        service = MarketingService(db)
        campaign = await service.pause_campaign(campaign_id)

        if not campaign:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

        await db.commit()
        return campaign

    except Exception as e:
        logger.error(f"Error pausing campaign: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== CAMPAIGN PERFORMANCE ENDPOINTS =====


@router.get("/campaigns/{campaign_id}/performance", response_model=CampaignPerformanceResponse)
async def get_campaign_performance(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
) -> CampaignPerformanceResponse:
    """Get campaign performance metrics."""
    try:
        performance = await marketing_agent.track_campaign_performance(db, campaign_id)
        return performance

    except Exception as e:
        logger.error(f"Error getting campaign performance: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/campaigns/{campaign_id}/optimize")
async def optimize_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get AI optimization suggestions for campaign."""
    try:
        suggestions = await marketing_agent.optimize_campaign(db, campaign_id)
        return suggestions

    except Exception as e:
        logger.error(f"Error optimizing campaign: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== CONTENT GENERATION ENDPOINTS =====


@router.post("/generate-job-ad/{requirement_id}", response_model=GenerateJobAdResponse)
async def generate_job_ad(
    requirement_id: int,
    platform: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> GenerateJobAdResponse:
    """Generate AI-optimized job advertisement."""
    try:
        ad = await marketing_agent.generate_job_ad(db, requirement_id, platform)
        return ad

    except Exception as e:
        logger.error(f"Error generating job ad: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/generate-bench-profile/{candidate_id}", response_model=GenerateBenchProfileResponse)
async def generate_bench_profile(
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
) -> GenerateBenchProfileResponse:
    """Generate anonymized bench profile for candidate."""
    try:
        profile = await marketing_agent.generate_bench_profile(db, candidate_id)
        return profile

    except Exception as e:
        logger.error(f"Error generating bench profile: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/generate-social-post", response_model=GenerateSocialPostResponse)
async def generate_social_post(
    request: GenerateSocialPostRequest,
    db: AsyncSession = Depends(get_db),
) -> GenerateSocialPostResponse:
    """Generate social media post."""
    try:
        post = await marketing_agent.generate_social_post(db, request.content_type, request.entity_id, request.platform)

        return GenerateSocialPostResponse(
            post_text=post,
            platform=request.platform,
            hashtags=[],
        )

    except Exception as e:
        logger.error(f"Error generating social post: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== HOTLIST ENDPOINTS =====


@router.post("/hotlists", response_model=HotlistResponse, status_code=status.HTTP_201_CREATED)
async def create_hotlist(
    hotlist_data: HotlistCreate,
    db: AsyncSession = Depends(get_db),
) -> HotlistResponse:
    """Create hotlist."""
    try:
        hotlist = await marketing_agent.create_hotlist(db, hotlist_data.model_dump())
        await db.commit()
        return hotlist

    except Exception as e:
        logger.error(f"Error creating hotlist: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/hotlists", response_model=PaginatedResponse[HotlistResponse])
async def list_hotlists(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[HotlistResponse]:
    """List hotlists."""
    try:
        service = MarketingService(db)
        hotlists, total = await service.get_hotlists(skip=skip, limit=limit)

        return PaginatedResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=hotlists,
        )

    except Exception as e:
        logger.error(f"Error listing hotlists: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/hotlists/{hotlist_id}", response_model=HotlistResponse)
async def update_hotlist(
    hotlist_id: int,
    hotlist_update: HotlistUpdate,
    db: AsyncSession = Depends(get_db),
) -> HotlistResponse:
    """Update hotlist."""
    try:
        service = MarketingService(db)
        hotlist = await service.update_hotlist(hotlist_id, hotlist_update.model_dump(exclude_unset=True))

        if not hotlist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotlist not found")

        await db.commit()
        return hotlist

    except Exception as e:
        logger.error(f"Error updating hotlist: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/hotlists/{hotlist_id}/share")
async def share_hotlist(
    hotlist_id: int,
    recipients: List[int],
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Share hotlist with customers."""
    try:
        service = MarketingService(db)
        hotlist = await service.update_hotlist(hotlist_id, {"shared_with": recipients})

        if not hotlist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotlist not found")

        await db.commit()

        return {
            "hotlist_id": hotlist_id,
            "shared_with": recipients,
            "message": f"Hotlist shared with {len(recipients)} recipients",
        }

    except Exception as e:
        logger.error(f"Error sharing hotlist: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== ANALYTICS ENDPOINTS =====


@router.get("/analytics", response_model=MarketingAnalyticsResponse)
async def get_marketing_analytics(
    db: AsyncSession = Depends(get_db),
) -> MarketingAnalyticsResponse:
    """Get overall marketing analytics."""
    try:
        analytics = await marketing_agent.get_marketing_analytics(db)
        return analytics

    except Exception as e:
        logger.error(f"Error getting marketing analytics: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== AUTO-PROMOTION ENDPOINTS =====


@router.post("/auto-promote")
async def auto_promote_urgent_requirements(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Auto-promote urgent requirements."""
    try:
        campaigns = await marketing_agent.auto_promote_urgent_requirements(db)
        await db.commit()

        return {
            "campaigns_created": len(campaigns),
            "campaign_ids": [c.id for c in campaigns],
        }

    except Exception as e:
        logger.error(f"Error auto-promoting: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
