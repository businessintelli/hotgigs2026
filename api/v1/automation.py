"""Automation rules and notifications API endpoints."""

import logging
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from schemas.automation import (
    AutomationRuleCreate,
    AutomationRuleUpdate,
    AutomationRuleResponse,
    AutomationRuleTestRequest,
    AutomationRuleTestResponse,
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationListResponse,
    NotificationUnreadCount,
    AutomationDashboardResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/automation")


# ===== AUTOMATION RULE ENDPOINTS =====

@router.post("/rules", response_model=AutomationRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_automation_rule(
    rule_data: AutomationRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> AutomationRuleResponse:
    """Create a new automation rule."""
    try:
        # Mock response
        return AutomationRuleResponse(
            id=1,
            name=rule_data.name,
            description=rule_data.description,
            trigger_event=rule_data.trigger_event,
            trigger_conditions=rule_data.trigger_conditions,
            action_type=rule_data.action_type,
            action_config=rule_data.action_config,
            is_enabled=rule_data.is_enabled,
            execution_count=0,
            last_triggered_at=None,
            created_by=current_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Error creating automation rule: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/rules", response_model=List[AutomationRuleResponse])
async def list_automation_rules(
    trigger: Optional[str] = Query(None, description="Filter by trigger event"),
    enabled_only: bool = Query(False, description="Show only enabled rules"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> List[AutomationRuleResponse]:
    """List automation rules with optional filtering."""
    try:
        # Mock data
        mock_rules = [
            AutomationRuleResponse(
                id=1,
                name="Auto-notify on submission",
                description="Send notification when submission is created",
                trigger_event="SUBMISSION_CREATED",
                trigger_conditions={"status": "created"},
                action_type="SEND_NOTIFICATION",
                action_config={"template": "submission_created", "recipients": ["recruiter"]},
                is_enabled=True,
                execution_count=42,
                last_triggered_at=datetime.utcnow(),
                created_by=current_user.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            AutomationRuleResponse(
                id=2,
                name="Update status on interview scheduled",
                description="Auto-update candidate status when interview is scheduled",
                trigger_event="INTERVIEW_SCHEDULED",
                trigger_conditions={"event": "interview_scheduled"},
                action_type="UPDATE_STATUS",
                action_config={"old_status": "SUBMITTED", "new_status": "INTERVIEW_SCHEDULED"},
                is_enabled=True,
                execution_count=18,
                last_triggered_at=datetime.utcnow(),
                created_by=current_user.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            AutomationRuleResponse(
                id=3,
                name="SLA breach alert",
                description="Alert when SLA is breached",
                trigger_event="SLA_BREACH",
                trigger_conditions={"metric": "response_time", "threshold_exceeded": True},
                action_type="SEND_EMAIL",
                action_config={"recipients": ["manager@company.com"], "template": "sla_breach_alert"},
                is_enabled=True,
                execution_count=5,
                last_triggered_at=datetime.utcnow(),
                created_by=current_user.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            AutomationRuleResponse(
                id=4,
                name="Compliance expiring soon",
                description="Notify when compliance document is expiring",
                trigger_event="COMPLIANCE_EXPIRING",
                trigger_conditions={"days_until_expiry": 30},
                action_type="CREATE_ACTIVITY",
                action_config={"activity_type": "compliance_warning", "priority": "HIGH"},
                is_enabled=False,
                execution_count=3,
                last_triggered_at=None,
                created_by=current_user.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
        ]

        # Filter by trigger if provided
        if trigger:
            mock_rules = [r for r in mock_rules if r.trigger_event == trigger]

        # Filter by enabled status if requested
        if enabled_only:
            mock_rules = [r for r in mock_rules if r.is_enabled]

        # Apply pagination
        return mock_rules[skip:skip + limit]

    except Exception as e:
        logger.error(f"Error listing automation rules: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/rules/{rule_id}", response_model=AutomationRuleResponse)
async def update_automation_rule(
    rule_id: int,
    rule_update: AutomationRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> AutomationRuleResponse:
    """Update an automation rule."""
    try:
        # Mock response
        return AutomationRuleResponse(
            id=rule_id,
            name=rule_update.name or f"Rule {rule_id}",
            description=rule_update.description,
            trigger_event="SUBMISSION_CREATED",
            trigger_conditions=rule_update.trigger_conditions or {},
            action_type="SEND_NOTIFICATION",
            action_config=rule_update.action_config or {},
            is_enabled=rule_update.is_enabled if rule_update.is_enabled is not None else True,
            execution_count=10,
            last_triggered_at=datetime.utcnow(),
            created_by=current_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Error updating automation rule: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_automation_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Delete an automation rule."""
    try:
        # Mock deletion
        return None

    except Exception as e:
        logger.error(f"Error deleting automation rule: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/rules/{rule_id}/test", response_model=AutomationRuleTestResponse)
async def test_automation_rule(
    rule_id: int,
    test_req: AutomationRuleTestRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> AutomationRuleTestResponse:
    """Test an automation rule with sample data (dry run)."""
    try:
        # Mock test response
        return AutomationRuleTestResponse(
            success=True,
            rule_id=rule_id,
            action_type="SEND_NOTIFICATION",
            would_execute=True,
            message="Rule would execute successfully with provided sample data",
            dry_run_output={
                "notification_sent_to": ["recruiter@company.com"],
                "message": "New submission received",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    except Exception as e:
        logger.error(f"Error testing automation rule: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== NOTIFICATION ENDPOINTS =====

@router.get("/notifications", response_model=NotificationListResponse)
async def list_notifications(
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    category: Optional[str] = Query(None, description="Filter by notification category"),
    notification_type: Optional[str] = Query(None, description="Filter by notification type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> NotificationListResponse:
    """List notifications for current user with optional filtering."""
    try:
        # Mock data
        mock_notifications = [
            NotificationResponse(
                id=1,
                user_id=current_user.id,
                title="New Submission Received",
                message="Candidate Alice Johnson submitted for Senior Developer role",
                notification_type="SUCCESS",
                category="SUBMISSION",
                reference_type="submission",
                reference_id=101,
                is_read=False,
                read_at=None,
                action_url="/submissions/101",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            NotificationResponse(
                id=2,
                user_id=current_user.id,
                title="Interview Scheduled",
                message="Bob Smith has interview scheduled for 2 days",
                notification_type="INFO",
                category="INTERVIEW",
                reference_type="interview",
                reference_id=202,
                is_read=False,
                read_at=None,
                action_url="/interviews/202",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            NotificationResponse(
                id=3,
                user_id=current_user.id,
                title="SLA Breach Alert",
                message="Response time SLA breached for requirement #5",
                notification_type="ALERT",
                category="SLA",
                reference_type="requirement",
                reference_id=5,
                is_read=True,
                read_at=datetime.utcnow(),
                action_url="/requirements/5",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            NotificationResponse(
                id=4,
                user_id=current_user.id,
                title="Compliance Document Expiring",
                message="Background check expires in 15 days for Diana Brown",
                notification_type="WARNING",
                category="COMPLIANCE",
                reference_type="compliance",
                reference_id=303,
                is_read=False,
                read_at=None,
                action_url="/compliance/303",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            NotificationResponse(
                id=5,
                user_id=current_user.id,
                title="Timesheet Submitted",
                message="Hannah Martinez submitted timesheet for week of Mar 3-9",
                notification_type="INFO",
                category="TIMESHEET",
                reference_type="timesheet",
                reference_id=404,
                is_read=True,
                read_at=datetime.utcnow(),
                action_url="/timesheets/404",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
        ]

        # Filter by read status
        if is_read is not None:
            mock_notifications = [n for n in mock_notifications if n.is_read == is_read]

        # Filter by category
        if category:
            mock_notifications = [n for n in mock_notifications if n.category == category]

        # Filter by notification type
        if notification_type:
            mock_notifications = [n for n in mock_notifications if n.notification_type == notification_type]

        # Count unread
        unread_count = sum(1 for n in mock_notifications if not n.is_read)

        # Apply pagination
        results = mock_notifications[skip:skip + limit]

        return NotificationListResponse(
            total=len(mock_notifications),
            unread_count=unread_count,
            notifications=results
        )

    except Exception as e:
        logger.error(f"Error listing notifications: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/notifications/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> NotificationResponse:
    """Mark a notification as read."""
    try:
        # Mock response
        return NotificationResponse(
            id=notification_id,
            user_id=current_user.id,
            title="Notification",
            message="This notification has been read",
            notification_type="INFO",
            category="SYSTEM",
            reference_type=None,
            reference_id=None,
            is_read=True,
            read_at=datetime.utcnow(),
            action_url=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/notifications/read-all", response_model=dict)
async def mark_all_notifications_as_read(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> dict:
    """Mark all notifications as read for current user."""
    try:
        # Mock response
        return {
            "success": True,
            "notifications_updated": 5,
            "message": "All notifications marked as read"
        }

    except Exception as e:
        logger.error(f"Error marking all notifications as read: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/notifications/unread-count", response_model=NotificationUnreadCount)
async def get_unread_notification_count(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> NotificationUnreadCount:
    """Get unread notification count for current user."""
    try:
        # Mock response
        return NotificationUnreadCount(
            unread_count=4,
            by_category={
                "SUBMISSION": 1,
                "INTERVIEW": 1,
                "COMPLIANCE": 1,
                "SLA": 1
            }
        )

    except Exception as e:
        logger.error(f"Error getting unread notification count: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== AUTOMATION DASHBOARD ENDPOINTS =====

@router.get("/dashboard", response_model=AutomationDashboardResponse)
async def get_automation_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> AutomationDashboardResponse:
    """Get automation dashboard with summary of rules and notifications."""
    try:
        # Mock dashboard data
        return AutomationDashboardResponse(
            active_rules_count=3,
            total_rules_count=4,
            recent_triggers=[
                {
                    "rule_id": 1,
                    "rule_name": "Auto-notify on submission",
                    "trigger_time": datetime.utcnow().isoformat(),
                    "entity_type": "submission",
                    "entity_id": 101,
                    "action_executed": "SEND_NOTIFICATION"
                },
                {
                    "rule_id": 2,
                    "rule_name": "Update status on interview scheduled",
                    "trigger_time": datetime.utcnow().isoformat(),
                    "entity_type": "interview",
                    "entity_id": 202,
                    "action_executed": "UPDATE_STATUS"
                },
                {
                    "rule_id": 3,
                    "rule_name": "SLA breach alert",
                    "trigger_time": datetime.utcnow().isoformat(),
                    "entity_type": "requirement",
                    "entity_id": 5,
                    "action_executed": "SEND_EMAIL"
                },
            ],
            notifications_summary={
                "total": 15,
                "unread": 4,
                "by_type": {
                    "INFO": 5,
                    "WARNING": 3,
                    "ALERT": 4,
                    "SUCCESS": 2,
                    "ACTION_REQUIRED": 1
                },
                "by_category": {
                    "SUBMISSION": 4,
                    "INTERVIEW": 3,
                    "OFFER": 2,
                    "COMPLIANCE": 3,
                    "SLA": 2,
                    "TIMESHEET": 1
                }
            },
            top_triggered_rules=[
                {
                    "rule_id": 1,
                    "rule_name": "Auto-notify on submission",
                    "execution_count": 42,
                    "last_triggered": datetime.utcnow().isoformat()
                },
                {
                    "rule_id": 2,
                    "rule_name": "Update status on interview scheduled",
                    "execution_count": 18,
                    "last_triggered": datetime.utcnow().isoformat()
                },
            ],
            last_updated=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Error getting automation dashboard: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


logger.info("Automation router initialized with 10 endpoints")
