import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user
from agents.referral_network_agent import ReferralNetworkAgent
from services.referral_service import ReferralService
from schemas.referral import (
    ReferrerSchema,
    ReferrerCreateSchema,
    ReferrerUpdateSchema,
    ReferralSchema,
    ReferralCreateSchema,
    ReferralMilestoneSchema,
    ReferralBonusSchema,
    ReferralBonusCreateSchema,
    ReferralBonusApproveSchema,
    ReferralBonusPaySchema,
    ReferralBonusConfigSchema,
    ReferralBonusConfigCreateSchema,
    ReferralDashboardSchema,
    ReferralEarningsSchema,
    NetworkAnalyticsSchema,
    HiddenRoleOpportunitySchema,
    ReferralOpportunityPushSchema,
    ReferralLinkSchema,
)
from schemas.common import PaginatedResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/referrals", tags=["referrals"])
agent = ReferralNetworkAgent()


@router.post("/register", response_model=ReferrerSchema, status_code=201)
async def register_referrer(
    referrer_data: ReferrerCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ReferrerSchema:
    """Register as referrer."""
    try:
        referrer = await agent.register_referrer(db, referrer_data.dict())
        return ReferrerSchema.from_orm(referrer)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error registering referrer: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/referrers/me", response_model=ReferrerSchema)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ReferrerSchema:
    """Get my referrer profile."""
    try:
        # Would fetch referrer by user_id
        referrer_id = current_user.get("referrer_id")
        if not referrer_id:
            raise HTTPException(status_code=403, detail="Not a registered referrer")

        referrer = await ReferralService.get_referrer(db, referrer_id)
        if not referrer:
            raise HTTPException(status_code=404, detail="Referrer not found")

        return referrer
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting referrer profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/referrers/me", response_model=ReferrerSchema)
async def update_my_profile(
    update_data: ReferrerUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ReferrerSchema:
    """Update my referrer profile."""
    try:
        referrer_id = current_user.get("referrer_id")
        if not referrer_id:
            raise HTTPException(status_code=403, detail="Not a registered referrer")

        referrer = await ReferralService.update_referrer(
            db, referrer_id, update_data.dict(exclude_unset=True)
        )
        return referrer
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating referrer profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/refer", response_model=ReferralSchema, status_code=201)
async def submit_referral(
    referral_data: ReferralCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ReferralSchema:
    """Submit a referral."""
    try:
        referrer_id = current_user.get("referrer_id")
        if not referrer_id:
            raise HTTPException(status_code=403, detail="Not a registered referrer")

        referral_dict = referral_data.dict()
        referral_dict["referrer_id"] = referrer_id

        referral = await agent.create_referral(
            db, referrer_id, referral_data.candidate_data, referral_data.requirement_id
        )
        return ReferralSchema.from_orm(referral)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting referral: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/my-referrals", response_model=PaginatedResponse[ReferralSchema])
async def get_my_referrals(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> PaginatedResponse[ReferralSchema]:
    """Get my referrals."""
    try:
        referrer_id = current_user.get("referrer_id")
        if not referrer_id:
            raise HTTPException(status_code=403, detail="Not a registered referrer")

        referrals, total = await ReferralService.list_referrals(
            db,
            referrer_id=referrer_id,
            status=status,
            skip=skip,
            limit=limit,
        )

        return PaginatedResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=referrals,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting my referrals: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/my-earnings", response_model=ReferralEarningsSchema)
async def get_my_earnings(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ReferralEarningsSchema:
    """Get my earnings dashboard."""
    try:
        referrer_id = current_user.get("referrer_id")
        if not referrer_id:
            raise HTTPException(status_code=403, detail="Not a registered referrer")

        # Fetch referrer and bonuses
        referrer = await ReferralService.get_referrer(db, referrer_id)
        if not referrer:
            raise HTTPException(status_code=404, detail="Referrer not found")

        bonuses = await ReferralService.list_referrer_bonuses(db, referrer_id)

        earnings = ReferralEarningsSchema(
            referrer_id=referrer_id,
            total_earnings=referrer.total_earnings,
            pending_earnings=referrer.pending_earnings,
            paid_earnings=referrer.total_earnings - referrer.pending_earnings,
            earned_bonuses=bonuses,
        )
        return earnings
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting earnings: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/my-bonuses", response_model=List[ReferralBonusSchema])
async def get_my_bonuses(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> List[ReferralBonusSchema]:
    """Get my bonus history."""
    try:
        referrer_id = current_user.get("referrer_id")
        if not referrer_id:
            raise HTTPException(status_code=403, detail="Not a registered referrer")

        bonuses = await ReferralService.list_referrer_bonuses(db, referrer_id, status)
        return bonuses
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting bonuses: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/hidden-roles", response_model=List[HiddenRoleOpportunitySchema])
async def get_hidden_roles(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> List[HiddenRoleOpportunitySchema]:
    """Browse hidden/unadvertised roles."""
    try:
        referrer_id = current_user.get("referrer_id")
        if not referrer_id:
            raise HTTPException(status_code=403, detail="Not a registered referrer")

        roles = await agent.get_hidden_roles(db, referrer_id)
        return roles
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting hidden roles: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/generate-link/{requirement_id}", response_model=ReferralLinkSchema)
async def generate_referral_link(
    requirement_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ReferralLinkSchema:
    """Generate shareable referral link."""
    try:
        referrer_id = current_user.get("referrer_id")
        if not referrer_id:
            raise HTTPException(status_code=403, detail="Not a registered referrer")

        referrer = await ReferralService.get_referrer(db, referrer_id)
        if not referrer:
            raise HTTPException(status_code=404, detail="Referrer not found")

        link = await agent.generate_referral_link(db, referrer_id, requirement_id)

        return ReferralLinkSchema(
            referral_link=link,
            referral_code=referrer.referral_code,
            requirement_id=requirement_id,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating referral link: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{referral_id}/milestone", response_model=ReferralBonusSchema)
async def record_milestone(
    referral_id: int,
    milestone_data: ReferralMilestoneSchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ReferralBonusSchema:
    """Record referral milestone (admin)."""
    try:
        # Check admin permission
        if current_user.get("role") not in ["admin", "manager"]:
            raise HTTPException(status_code=403, detail="Not authorized")

        bonus = await agent.process_referral_milestone(
            db, referral_id, milestone_data.milestone
        )

        if bonus:
            return ReferralBonusSchema.from_orm(bonus)
        return {}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error recording milestone: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/bonuses/{bonus_id}/approve", response_model=ReferralBonusSchema)
async def approve_bonus(
    bonus_id: int,
    approve_data: ReferralBonusApproveSchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ReferralBonusSchema:
    """Approve bonus (admin)."""
    try:
        if current_user.get("role") not in ["admin", "manager"]:
            raise HTTPException(status_code=403, detail="Not authorized")

        bonus = await ReferralService.approve_bonus(
            db, bonus_id, current_user["id"], approve_data.notes
        )
        return bonus
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error approving bonus: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/bonuses/{bonus_id}/pay", response_model=ReferralBonusSchema)
async def mark_bonus_paid(
    bonus_id: int,
    pay_data: ReferralBonusPaySchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ReferralBonusSchema:
    """Mark bonus as paid (admin)."""
    try:
        if current_user.get("role") not in ["admin", "manager"]:
            raise HTTPException(status_code=403, detail="Not authorized")

        bonus = await ReferralService.mark_bonus_paid(
            db, bonus_id, pay_data.payment_reference, pay_data.notes
        )
        return bonus
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error marking bonus paid: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/leaderboard", response_model=List[dict])
async def get_leaderboard(
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> List[dict]:
    """Get referrer leaderboard."""
    try:
        leaderboard = await ReferralService.get_leaderboard(db, limit)
        return leaderboard
    except Exception as e:
        logger.error(f"Error getting leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analytics", response_model=NetworkAnalyticsSchema)
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> NetworkAnalyticsSchema:
    """Get network analytics."""
    try:
        if current_user.get("role") not in ["admin", "manager", "recruiter"]:
            raise HTTPException(status_code=403, detail="Not authorized")

        analytics = await agent.get_network_analytics(db)
        return analytics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/push-opportunity", response_model=List[dict])
async def push_opportunity(
    push_data: ReferralOpportunityPushSchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> List[dict]:
    """Push opportunity to referrers."""
    try:
        if current_user.get("role") not in ["admin", "manager", "recruiter"]:
            raise HTTPException(status_code=403, detail="Not authorized")

        results = await agent.send_referral_opportunity(
            db, push_data.referrer_ids, push_data.requirement_id
        )
        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pushing opportunity: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/bonus-configs", response_model=List[ReferralBonusConfigSchema])
async def list_bonus_configs(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> List[ReferralBonusConfigSchema]:
    """List bonus configurations."""
    try:
        # Placeholder: would fetch from database
        return []
    except Exception as e:
        logger.error(f"Error listing bonus configs: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/bonus-configs", response_model=ReferralBonusConfigSchema, status_code=201)
async def create_bonus_config(
    config_data: ReferralBonusConfigCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ReferralBonusConfigSchema:
    """Create bonus configuration."""
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")

        result = await ReferralService.create_bonus_config(db, config_data.dict())
        return ReferralBonusConfigSchema(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating bonus config: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
