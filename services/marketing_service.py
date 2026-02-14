"""Digital marketing service."""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models.marketing import MarketingCampaign, Hotlist, CampaignDistribution, EmailCampaignTracking

logger = logging.getLogger(__name__)


class MarketingService:
    """Service for marketing operations."""

    def __init__(self, db: AsyncSession):
        """Initialize marketing service."""
        self.db = db

    async def get_campaigns(self, skip: int = 0, limit: int = 20) -> tuple[List[MarketingCampaign], int]:
        """Get all marketing campaigns with pagination."""
        try:
            stmt = select(func.count(MarketingCampaign.id))
            result = await self.db.execute(stmt)
            total = result.scalar() or 0

            stmt = (
                select(MarketingCampaign)
                .offset(skip)
                .limit(limit)
                .order_by(MarketingCampaign.created_at.desc())
            )
            result = await self.db.execute(stmt)
            campaigns = result.scalars().all()

            return campaigns, total

        except Exception as e:
            logger.error(f"Error getting campaigns: {str(e)}")
            raise

    async def get_campaign_by_id(self, campaign_id: int) -> Optional[MarketingCampaign]:
        """Get marketing campaign by ID."""
        try:
            stmt = select(MarketingCampaign).where(MarketingCampaign.id == campaign_id)
            result = await self.db.execute(stmt)
            return result.scalars().first()

        except Exception as e:
            logger.error(f"Error getting campaign: {str(e)}")
            raise

    async def update_campaign(self, campaign_id: int, update_data: Dict[str, Any]) -> Optional[MarketingCampaign]:
        """Update marketing campaign."""
        try:
            campaign = await self.get_campaign_by_id(campaign_id)
            if not campaign:
                return None

            for key, value in update_data.items():
                if hasattr(campaign, key) and value is not None:
                    setattr(campaign, key, value)

            await self.db.flush()
            logger.info(f"Updated campaign {campaign_id}")
            return campaign

        except Exception as e:
            logger.error(f"Error updating campaign: {str(e)}")
            raise

    async def pause_campaign(self, campaign_id: int) -> Optional[MarketingCampaign]:
        """Pause a marketing campaign."""
        try:
            campaign = await self.get_campaign_by_id(campaign_id)
            if campaign:
                campaign.status = "paused"
                await self.db.flush()
                logger.info(f"Paused campaign {campaign_id}")
            return campaign

        except Exception as e:
            logger.error(f"Error pausing campaign: {str(e)}")
            raise

    async def resume_campaign(self, campaign_id: int) -> Optional[MarketingCampaign]:
        """Resume a paused marketing campaign."""
        try:
            campaign = await self.get_campaign_by_id(campaign_id)
            if campaign:
                campaign.status = "active"
                await self.db.flush()
                logger.info(f"Resumed campaign {campaign_id}")
            return campaign

        except Exception as e:
            logger.error(f"Error resuming campaign: {str(e)}")
            raise

    async def get_hotlists(self, skip: int = 0, limit: int = 20) -> tuple[List[Hotlist], int]:
        """Get all hotlists with pagination."""
        try:
            stmt = select(func.count(Hotlist.id))
            result = await self.db.execute(stmt)
            total = result.scalar() or 0

            stmt = select(Hotlist).offset(skip).limit(limit).order_by(Hotlist.created_at.desc())
            result = await self.db.execute(stmt)
            hotlists = result.scalars().all()

            return hotlists, total

        except Exception as e:
            logger.error(f"Error getting hotlists: {str(e)}")
            raise

    async def get_hotlist_by_id(self, hotlist_id: int) -> Optional[Hotlist]:
        """Get hotlist by ID."""
        try:
            stmt = select(Hotlist).where(Hotlist.id == hotlist_id)
            result = await self.db.execute(stmt)
            return result.scalars().first()

        except Exception as e:
            logger.error(f"Error getting hotlist: {str(e)}")
            raise

    async def update_hotlist(self, hotlist_id: int, update_data: Dict[str, Any]) -> Optional[Hotlist]:
        """Update hotlist."""
        try:
            hotlist = await self.get_hotlist_by_id(hotlist_id)
            if not hotlist:
                return None

            for key, value in update_data.items():
                if hasattr(hotlist, key) and value is not None:
                    setattr(hotlist, key, value)

            await self.db.flush()
            logger.info(f"Updated hotlist {hotlist_id}")
            return hotlist

        except Exception as e:
            logger.error(f"Error updating hotlist: {str(e)}")
            raise

    async def get_campaign_distributions(
        self, campaign_id: int, skip: int = 0, limit: int = 20
    ) -> tuple[List[CampaignDistribution], int]:
        """Get campaign distributions."""
        try:
            stmt = select(func.count(CampaignDistribution.id)).where(CampaignDistribution.campaign_id == campaign_id)
            result = await self.db.execute(stmt)
            total = result.scalar() or 0

            stmt = (
                select(CampaignDistribution)
                .where(CampaignDistribution.campaign_id == campaign_id)
                .offset(skip)
                .limit(limit)
                .order_by(CampaignDistribution.created_at.desc())
            )
            result = await self.db.execute(stmt)
            distributions = result.scalars().all()

            return distributions, total

        except Exception as e:
            logger.error(f"Error getting campaign distributions: {str(e)}")
            raise

    async def get_email_tracking(
        self, campaign_id: int, skip: int = 0, limit: int = 50
    ) -> tuple[List[EmailCampaignTracking], int]:
        """Get email tracking for campaign."""
        try:
            stmt = select(func.count(EmailCampaignTracking.id)).where(EmailCampaignTracking.campaign_id == campaign_id)
            result = await self.db.execute(stmt)
            total = result.scalar() or 0

            stmt = (
                select(EmailCampaignTracking)
                .where(EmailCampaignTracking.campaign_id == campaign_id)
                .offset(skip)
                .limit(limit)
                .order_by(EmailCampaignTracking.created_at.desc())
            )
            result = await self.db.execute(stmt)
            tracking = result.scalars().all()

            return tracking, total

        except Exception as e:
            logger.error(f"Error getting email tracking: {str(e)}")
            raise

    async def increment_campaign_impressions(self, campaign_id: int, count: int = 1) -> None:
        """Increment campaign impressions."""
        try:
            campaign = await self.get_campaign_by_id(campaign_id)
            if campaign:
                campaign.impressions += count
                await self.db.flush()

        except Exception as e:
            logger.error(f"Error incrementing impressions: {str(e)}")
            raise

    async def increment_campaign_clicks(self, campaign_id: int, count: int = 1) -> None:
        """Increment campaign clicks."""
        try:
            campaign = await self.get_campaign_by_id(campaign_id)
            if campaign:
                campaign.clicks += count
                await self.db.flush()

        except Exception as e:
            logger.error(f"Error incrementing clicks: {str(e)}")
            raise

    async def increment_campaign_applications(self, campaign_id: int, count: int = 1) -> None:
        """Increment campaign applications."""
        try:
            campaign = await self.get_campaign_by_id(campaign_id)
            if campaign:
                campaign.applications += count
                await self.db.flush()

        except Exception as e:
            logger.error(f"Error incrementing applications: {str(e)}")
            raise

    async def increment_campaign_conversions(self, campaign_id: int, count: int = 1) -> None:
        """Increment campaign conversions."""
        try:
            campaign = await self.get_campaign_by_id(campaign_id)
            if campaign:
                campaign.conversions += count
                await self.db.flush()

        except Exception as e:
            logger.error(f"Error incrementing conversions: {str(e)}")
            raise

    async def update_email_tracking(self, tracking_id: int, update_data: Dict[str, Any]) -> None:
        """Update email tracking record."""
        try:
            stmt = select(EmailCampaignTracking).where(EmailCampaignTracking.id == tracking_id)
            result = await self.db.execute(stmt)
            tracking = result.scalars().first()

            if tracking:
                for key, value in update_data.items():
                    if hasattr(tracking, key) and value is not None:
                        setattr(tracking, key, value)
                await self.db.flush()

        except Exception as e:
            logger.error(f"Error updating email tracking: {str(e)}")
            raise
