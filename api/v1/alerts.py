"""Alerts and notifications API endpoints."""

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db
from schemas.alerts import (
    AlertRuleCreate,
    AlertRuleUpdate,
    AlertRuleResponse,
    NotificationCreate,
    NotificationResponse,
    NotificationListResponse,
    NotificationPreferenceUpdate,
    NotificationPreferenceResponse,
    DigestNotificationResponse,
    AlertAnalyticsResponse,
)
from schemas.common import PaginatedResponse
from services.alerts_service import AlertsService
from agents.alerts_notification_agent import AlertsNotificationAgent
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alerts", tags=["alerts"])
alerts_agent = AlertsNotificationAgent(anthropic_api_key=settings.anthropic_api_key)


# ===== ALERT RULE ENDPOINTS =====


@router.post("/rules", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_alert_rule(
    rule_data: AlertRuleCreate,
    db: AsyncSession = Depends(get_db),
) -> AlertRuleResponse:
    """Create configurable alert rule."""
    try:
        rule = await alerts_agent.create_alert_rule(db, rule_data.model_dump())
        await db.commit()
        return rule

    except Exception as e:
        logger.error(f"Error creating alert rule: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/rules", response_model=PaginatedResponse[AlertRuleResponse])
async def list_alert_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[AlertRuleResponse]:
    """List alert rules."""
    try:
        service = AlertsService(db)
        rules, total = await service.get_rules(skip=skip, limit=limit)

        return PaginatedResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=rules,
        )

    except Exception as e:
        logger.error(f"Error listing alert rules: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/rules/{rule_id}", response_model=AlertRuleResponse)
async def get_alert_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
) -> AlertRuleResponse:
    """Get alert rule details."""
    try:
        service = AlertsService(db)
        rule = await service.get_rule_by_id(rule_id)

        if not rule:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")

        return rule

    except Exception as e:
        logger.error(f"Error getting alert rule: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/rules/{rule_id}", response_model=AlertRuleResponse)
async def update_alert_rule(
    rule_id: int,
    rule_update: AlertRuleUpdate,
    db: AsyncSession = Depends(get_db),
) -> AlertRuleResponse:
    """Update alert rule."""
    try:
        service = AlertsService(db)
        rule = await service.update_rule(rule_id, rule_update.model_dump(exclude_unset=True))

        if not rule:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")

        await db.commit()
        return rule

    except Exception as e:
        logger.error(f"Error updating alert rule: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/rules/{rule_id}")
async def deactivate_alert_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Deactivate alert rule."""
    try:
        service = AlertsService(db)
        rule = await service.deactivate_rule(rule_id)

        if not rule:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")

        await db.commit()

        return {"message": "Alert rule deactivated", "rule_id": rule_id}

    except Exception as e:
        logger.error(f"Error deactivating alert rule: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/rules/{rule_id}/test")
async def test_alert_rule(
    rule_id: int,
    sample_event: dict,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Test an alert rule with sample event."""
    try:
        service = AlertsService(db)
        rule = await service.get_rule_by_id(rule_id)

        if not rule:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")

        # Check if conditions match
        conditions_match = await alerts_agent._evaluate_conditions(rule.conditions, sample_event)

        return {
            "rule_id": rule_id,
            "conditions_match": conditions_match,
            "notification_channels": rule.notification_channels,
            "message": "Rule test completed",
        }

    except Exception as e:
        logger.error(f"Error testing alert rule: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== NOTIFICATION ENDPOINTS =====


@router.get("/notifications", response_model=NotificationListResponse)
async def get_my_notifications(
    user_id: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
) -> NotificationListResponse:
    """Get my notifications."""
    try:
        service = AlertsService(db)
        notifications, total = await service.get_notifications(
            user_id=user_id, skip=skip, limit=limit, unread_only=unread_only
        )
        unread_count = await service.get_unread_count(user_id)

        return NotificationListResponse(
            notifications=notifications,
            total=total,
            unread_count=unread_count,
        )

    except Exception as e:
        logger.error(f"Error getting notifications: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/notifications/unread-count")
async def get_unread_count(
    user_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get unread notification count."""
    try:
        service = AlertsService(db)
        unread_count = await service.get_unread_count(user_id)

        return {"user_id": user_id, "unread_count": unread_count}

    except Exception as e:
        logger.error(f"Error getting unread count: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Mark notification as read."""
    try:
        service = AlertsService(db)
        notification = await service.mark_read(notification_id)

        if not notification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

        await db.commit()

        return {"notification_id": notification_id, "message": "Marked as read"}

    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/notifications/read-all")
async def mark_all_read(
    user_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Mark all notifications as read."""
    try:
        service = AlertsService(db)
        count = await service.mark_all_read(user_id)
        await db.commit()

        return {"user_id": user_id, "marked_as_read": count}

    except Exception as e:
        logger.error(f"Error marking all as read: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== NOTIFICATION DIGEST ENDPOINTS =====


@router.get("/notifications/digest", response_model=DigestNotificationResponse)
async def get_digest(
    user_id: int = Query(...),
    period: str = Query("daily", description="daily/weekly"),
    db: AsyncSession = Depends(get_db),
) -> DigestNotificationResponse:
    """Get notification digest."""
    try:
        digest = await alerts_agent.get_digest(db, user_id, period)

        return DigestNotificationResponse(
            digest_period=period,
            notifications_count=digest.get("total_notifications", 0),
            critical_notifications=digest.get("by_priority", {}).get("critical", []),
            high_notifications=digest.get("by_priority", {}).get("high", []),
            medium_notifications=digest.get("by_priority", {}).get("medium", []),
            low_notifications=digest.get("by_priority", {}).get("low", []),
            generated_at=digest.get("generated_at"),
        )

    except Exception as e:
        logger.error(f"Error getting digest: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== NOTIFICATION PREFERENCES ENDPOINTS =====


@router.get("/notifications/preferences", response_model=NotificationPreferenceResponse)
async def get_my_preferences(
    user_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
) -> NotificationPreferenceResponse:
    """Get my notification preferences."""
    try:
        service = AlertsService(db)
        preferences = await service.get_preferences(user_id)

        if not preferences:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preferences not found")

        return preferences

    except Exception as e:
        logger.error(f"Error getting preferences: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/notifications/preferences", response_model=NotificationPreferenceResponse)
async def update_my_preferences(
    user_id: int = Query(...),
    preferences_update: NotificationPreferenceUpdate = None,
    db: AsyncSession = Depends(get_db),
) -> NotificationPreferenceResponse:
    """Update my notification preferences."""
    try:
        service = AlertsService(db)
        preferences = await service.update_preferences(
            user_id, preferences_update.model_dump(exclude_unset=True) if preferences_update else {}
        )

        if not preferences:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preferences not found")

        await db.commit()
        return preferences

    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== ANALYTICS ENDPOINTS =====


@router.get("/analytics", response_model=AlertAnalyticsResponse)
async def get_alert_analytics(
    db: AsyncSession = Depends(get_db),
) -> AlertAnalyticsResponse:
    """Get alert analytics."""
    try:
        analytics = await alerts_agent.get_alert_analytics(db)
        return analytics

    except Exception as e:
        logger.error(f"Error getting alert analytics: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
