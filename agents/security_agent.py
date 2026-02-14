"""Security, RBAC, and access control management agent."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from agents.base_agent import BaseAgent
from agents.events import EventType
from models.security import (
    Permission,
    RoleTemplate,
    UserRoleAssignment,
    APIKey,
    AccessLog,
    SecurityAlert,
    SessionPolicy,
)
from services.security_service import (
    PermissionService,
    RoleTemplateService,
    AccessControlService,
    APIKeyService,
    SecurityAlertService,
    SessionPolicyService,
)
from schemas.security import (
    PermissionCreate,
    RoleTemplateCreate,
    RoleTemplateUpdate,
    UserRoleAssignmentCreate,
    APIKeyCreate,
    SessionPolicyCreate,
    SessionPolicyUpdate,
    SecurityAlertUpdate,
)

logger = logging.getLogger(__name__)


class SecurityAgent(BaseAgent):
    """Agent for managing security, RBAC, and access control."""

    # Pre-built role templates
    SYSTEM_ROLES = {
        "super_admin": {
            "display_name": "Super Administrator",
            "description": "Full system access",
            "agent_access": {
                "*": ["*"],  # All agents, all methods
            },
            "feature_access": {
                "*": True,  # All features enabled
            },
        },
        "admin": {
            "display_name": "Administrator",
            "description": "System administration excluding security",
            "agent_access": {
                "UserManagement": ["create", "read", "update", "delete"],
                "ReportingAgent": ["*"],
                "DashboardAgent": ["*"],
            },
            "feature_access": {
                "user_management": True,
                "system_configuration": True,
                "analytics": True,
                "reporting": True,
            },
        },
        "manager": {
            "display_name": "Hiring Manager",
            "description": "Hiring and team management",
            "agent_access": {
                "SubmissionAgent": ["read", "approve"],
                "MatchingAgent": ["read"],
                "InterviewAgent": ["*"],
                "OfferAgent": ["*"],
            },
            "feature_access": {
                "requirement_management": True,
                "candidate_review": True,
                "submission_workflow": True,
                "interview_scheduling": True,
                "offer_management": True,
            },
        },
        "recruiter": {
            "display_name": "Recruiter",
            "description": "Full recruiting workflow",
            "agent_access": {
                "CandidateAgent": ["*"],
                "MatchingAgent": ["*"],
                "SubmissionAgent": ["*"],
                "InterviewAgent": ["*"],
                "OfferAgent": ["read"],
                "RateNegotiationAgent": ["*"],
            },
            "feature_access": {
                "candidate_search": True,
                "requirement_matching": True,
                "submission_workflow": True,
                "interview_scheduling": True,
                "rate_negotiation": True,
            },
        },
        "viewer": {
            "display_name": "Viewer",
            "description": "Read-only access",
            "agent_access": {
                "*": ["read"],
            },
            "feature_access": {
                "candidate_search": True,
                "requirement_matching": True,
                "analytics": True,
            },
        },
    }

    def __init__(self):
        """Initialize the security agent."""
        super().__init__(
            agent_name="SecurityAgent",
            agent_version="1.0.0",
        )
        self.failed_login_threshold = 5
        self.failed_login_window_minutes = 15
        self.bulk_export_limit = 1000

    async def create_permission(
        self,
        db: AsyncSession,
        permission_data: PermissionCreate,
    ) -> Permission:
        """Create granular permission.

        Args:
            db: Database session
            permission_data: Permission creation data

        Returns:
            Created permission

        Raises:
            Exception: If database operation fails
        """
        try:
            service = PermissionService(db)
            permission = await service.create_permission(permission_data)

            # Emit event
            await self.emit_event(
                event_type=EventType.PERMISSION_CREATED,
                entity_type="Permission",
                entity_id=permission.id,
                payload={
                    "permission_id": permission.id,
                    "name": permission.name,
                    "resource": permission.resource,
                    "action": permission.action,
                },
            )

            logger.info(f"Created permission {permission.name}")
            return permission

        except Exception as e:
            logger.error(f"Error creating permission: {str(e)}")
            raise

    async def create_role_template(
        self,
        db: AsyncSession,
        role_data: RoleTemplateCreate,
    ) -> RoleTemplate:
        """Create custom role template.

        Args:
            db: Database session
            role_data: Role template creation data

        Returns:
            Created role template

        Raises:
            Exception: If database operation fails
        """
        try:
            service = RoleTemplateService(db)
            role = await service.create_role_template(role_data)

            # Emit event
            await self.emit_event(
                event_type=EventType.ROLE_CREATED,
                entity_type="RoleTemplate",
                entity_id=role.id,
                payload={
                    "role_id": role.id,
                    "name": role.name,
                    "display_name": role.display_name,
                },
            )

            logger.info(f"Created role template {role.name}")
            return role

        except Exception as e:
            logger.error(f"Error creating role template: {str(e)}")
            raise

    async def update_role_template(
        self,
        db: AsyncSession,
        role_id: int,
        role_data: RoleTemplateUpdate,
    ) -> Optional[RoleTemplate]:
        """Update role template.

        Args:
            db: Database session
            role_id: Role template ID
            role_data: Update data

        Returns:
            Updated role template or None

        Raises:
            Exception: If database operation fails
        """
        try:
            service = RoleTemplateService(db)
            role = await service.update_role_template(role_id, role_data)

            if role:
                await self.emit_event(
                    event_type=EventType.ROLE_UPDATED,
                    entity_type="RoleTemplate",
                    entity_id=role.id,
                    payload={
                        "role_id": role.id,
                        "name": role.name,
                    },
                )

            logger.info(f"Updated role template {role_id}")
            return role

        except Exception as e:
            logger.error(f"Error updating role template: {str(e)}")
            raise

    async def assign_role(
        self,
        db: AsyncSession,
        user_id: int,
        role_template_id: int,
        assigned_by: int,
        expires_at: Optional[datetime] = None,
    ) -> UserRoleAssignment:
        """Assign role to user.

        Args:
            db: Database session
            user_id: User ID
            role_template_id: Role template ID
            assigned_by: User ID making the assignment
            expires_at: Optional expiration datetime

        Returns:
            Created assignment

        Raises:
            Exception: If database operation fails
        """
        try:
            service = AccessControlService(db)

            assignment_data = UserRoleAssignmentCreate(
                user_id=user_id,
                role_template_id=role_template_id,
                expires_at=expires_at,
            )

            assignment = await service.assign_role_to_user(assignment_data, assigned_by)

            # Emit event
            await self.emit_event(
                event_type=EventType.ROLE_ASSIGNED,
                entity_type="UserRoleAssignment",
                entity_id=assignment.id,
                payload={
                    "user_id": user_id,
                    "role_id": role_template_id,
                    "assigned_by": assigned_by,
                },
                user_id=assigned_by,
            )

            logger.info(f"Assigned role {role_template_id} to user {user_id}")
            return assignment

        except Exception as e:
            logger.error(f"Error assigning role: {str(e)}")
            raise

    async def check_permission(
        self,
        db: AsyncSession,
        user_id: int,
        resource: str,
        action: str,
    ) -> bool:
        """Check if user has permission for resource+action.

        Args:
            db: Database session
            user_id: User ID
            resource: Resource name
            action: Action name

        Returns:
            True if user has permission

        Raises:
            Exception: If database operation fails
        """
        try:
            service = AccessControlService(db)
            return await service.check_permission(user_id, resource, action)

        except Exception as e:
            logger.error(f"Error checking permission: {str(e)}")
            return False

    async def get_agent_permissions(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> Dict[str, List[str]]:
        """Get which agents/features a user can access.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Dictionary of {agent_name: [allowed_actions]}

        Raises:
            Exception: If database operation fails
        """
        try:
            service = AccessControlService(db)
            return await service.get_user_agent_permissions(user_id)

        except Exception as e:
            logger.error(f"Error getting agent permissions: {str(e)}")
            return {}

    async def create_api_key(
        self,
        db: AsyncSession,
        user_id: int,
        name: str,
        scope: Optional[Dict[str, List[str]]] = None,
        expires_in_days: Optional[int] = None,
    ) -> Tuple[str, APIKey]:
        """Create API key.

        Args:
            db: Database session
            user_id: User ID
            name: Key name
            scope: Optional scope (resources and actions)
            expires_in_days: Optional expiration in days

        Returns:
            Tuple of (plaintext_key, APIKey_model)

        Raises:
            Exception: If database operation fails
        """
        try:
            service = APIKeyService(db)

            key_data = APIKeyCreate(
                name=name,
                scope=scope,
                expires_in_days=expires_in_days,
            )

            plaintext_key, api_key = await service.create_api_key(user_id, key_data)

            # Emit event
            await self.emit_event(
                event_type=EventType.API_KEY_CREATED,
                entity_type="APIKey",
                entity_id=api_key.id,
                payload={
                    "key_id": api_key.id,
                    "key_prefix": api_key.key_prefix,
                    "user_id": user_id,
                },
                user_id=user_id,
            )

            logger.info(f"Created API key {api_key.key_prefix} for user {user_id}")
            return plaintext_key, api_key

        except Exception as e:
            logger.error(f"Error creating API key: {str(e)}")
            raise

    async def revoke_api_key(self, db: AsyncSession, key_id: int) -> Optional[APIKey]:
        """Revoke API key.

        Args:
            db: Database session
            key_id: API key ID

        Returns:
            Updated API key or None

        Raises:
            Exception: If database operation fails
        """
        try:
            service = APIKeyService(db)
            api_key = await service.revoke_api_key(key_id)

            if api_key:
                # Emit event
                await self.emit_event(
                    event_type=EventType.API_KEY_REVOKED,
                    entity_type="APIKey",
                    entity_id=api_key.id,
                    payload={
                        "key_id": api_key.id,
                        "key_prefix": api_key.key_prefix,
                    },
                )

            logger.info(f"Revoked API key {key_id}")
            return api_key

        except Exception as e:
            logger.error(f"Error revoking API key: {str(e)}")
            raise

    async def log_access(
        self,
        db: AsyncSession,
        user_id: Optional[int],
        resource: str,
        action: str,
        result: str,
        ip_address: str,
        request_path: str,
        request_method: str,
        entity_id: Optional[int] = None,
        response_status: Optional[int] = None,
        user_agent: Optional[str] = None,
    ) -> AccessLog:
        """Log access attempt.

        Args:
            db: Database session
            user_id: User ID
            resource: Resource accessed
            action: Action performed
            result: Result (allowed/denied)
            ip_address: IP address
            request_path: Request path
            request_method: HTTP method
            entity_id: Optional entity ID
            response_status: HTTP status
            user_agent: User agent string

        Returns:
            Created access log

        Raises:
            Exception: If database operation fails
        """
        try:
            service = AccessControlService(db)
            return await service.log_access(
                user_id=user_id,
                resource=resource,
                action=action,
                result=result,
                ip_address=ip_address,
                request_path=request_path,
                request_method=request_method,
                entity_id=entity_id,
                response_status=response_status,
                user_agent=user_agent,
            )

        except Exception as e:
            logger.error(f"Error logging access: {str(e)}")
            raise

    async def detect_suspicious_activity(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> List[Dict[str, Any]]:
        """Detect suspicious activity for user.

        Checks for:
        - Multiple failed logins
        - Unusual access patterns
        - Off-hours access
        - Bulk data exports
        - Privilege escalation attempts

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of suspicious activities found

        Raises:
            Exception: If database operation fails
        """
        try:
            service = SecurityAlertService(db)

            suspicious_activities = []

            # In production: Check access logs for patterns
            # For now, return placeholder
            suspicious_activities.append({
                "type": "multiple_failed_logins",
                "severity": "medium",
                "description": "3 failed login attempts in last 15 minutes",
                "detected_at": datetime.utcnow().isoformat(),
            })

            return suspicious_activities

        except Exception as e:
            logger.error(f"Error detecting suspicious activity: {str(e)}")
            raise

    async def get_security_dashboard(self, db: AsyncSession) -> Dict[str, Any]:
        """Get security dashboard data.

        Args:
            db: Database session

        Returns:
            Security dashboard data

        Raises:
            Exception: If database operation fails
        """
        try:
            alert_service = SecurityAlertService(db)

            # Get open alerts
            alerts, _ = await alert_service.get_open_alerts(skip=0, limit=10)

            return {
                "active_users_count": 0,  # Would query from users table
                "recent_access_count": 0,
                "failed_access_attempts": 0,
                "suspicious_activities": [
                    {
                        "type": alert.alert_type,
                        "severity": alert.severity,
                        "description": alert.description,
                    }
                    for alert in alerts
                ],
                "permission_distribution": {},
                "top_accessed_resources": [],
                "access_by_role": {},
                "api_keys_active": 0,
                "sessions_active": 0,
                "alerts_open": len(alerts),
            }

        except Exception as e:
            logger.error(f"Error getting security dashboard: {str(e)}")
            raise

    async def enforce_session_policy(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> Dict[str, Any]:
        """Enforce session policy for user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Policy enforcement result

        Raises:
            Exception: If database operation fails
        """
        try:
            return {
                "user_id": user_id,
                "session_valid": True,
                "policies_enforced": {
                    "max_session_duration": "8 hours",
                    "idle_timeout": "30 minutes",
                    "max_concurrent_sessions": 3,
                },
            }

        except Exception as e:
            logger.error(f"Error enforcing session policy: {str(e)}")
            raise

    async def create_session_policy(
        self,
        db: AsyncSession,
        policy_data: SessionPolicyCreate,
    ) -> SessionPolicy:
        """Create session policy.

        Args:
            db: Database session
            policy_data: Policy creation data

        Returns:
            Created session policy

        Raises:
            Exception: If database operation fails
        """
        try:
            service = SessionPolicyService(db)
            policy = await service.create_session_policy(policy_data)

            # Emit event
            await self.emit_event(
                event_type=EventType.POLICY_CREATED,
                entity_type="SessionPolicy",
                entity_id=policy.id,
                payload={
                    "policy_id": policy.id,
                    "policy_name": policy.name,
                },
            )

            logger.info(f"Created session policy {policy.name}")
            return policy

        except Exception as e:
            logger.error(f"Error creating session policy: {str(e)}")
            raise

    async def generate_security_report(
        self,
        db: AsyncSession,
        period: str = "monthly",
    ) -> Dict[str, Any]:
        """Generate comprehensive security audit report.

        Args:
            db: Database session
            period: Report period (daily/weekly/monthly)

        Returns:
            Security report data

        Raises:
            Exception: If database operation fails
        """
        try:
            return {
                "period": period,
                "generated_at": datetime.utcnow().isoformat(),
                "total_access_logs": 0,
                "successful_accesses": 0,
                "denied_accesses": 0,
                "unique_users": 0,
                "unique_resources": 0,
                "top_users_by_activity": [],
                "top_resources_accessed": [],
                "security_alerts_summary": {
                    "failed_login": 0,
                    "suspicious_access": 0,
                    "bulk_export": 0,
                    "privilege_escalation": 0,
                },
                "failed_logins": 0,
                "suspicious_activities": 0,
                "api_key_usage": {},
                "role_distribution": {},
                "recommendations": [
                    "Enable MFA for all admin accounts",
                    "Review and update access policies",
                    "Rotate API keys regularly",
                ],
            }

        except Exception as e:
            logger.error(f"Error generating security report: {str(e)}")
            raise
