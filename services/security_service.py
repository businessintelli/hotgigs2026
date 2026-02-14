"""Security, RBAC, and access control service."""

import logging
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from models.security import (
    Permission,
    RoleTemplate,
    UserRoleAssignment,
    APIKey,
    AccessLog,
    SecurityAlert,
    SessionPolicy,
)
from schemas.security import (
    PermissionCreate,
    RoleTemplateCreate,
    RoleTemplateUpdate,
    UserRoleAssignmentCreate,
    APIKeyCreate,
    SessionPolicyCreate,
    SessionPolicyUpdate,
)

logger = logging.getLogger(__name__)


class PermissionService:
    """Service for permission management."""

    def __init__(self, db: AsyncSession):
        """Initialize service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_permission(self, permission_data: PermissionCreate) -> Permission:
        """Create permission.

        Args:
            permission_data: Permission creation data

        Returns:
            Created permission

        Raises:
            Exception: If database operation fails
        """
        try:
            permission = Permission(
                name=permission_data.name,
                resource=permission_data.resource,
                action=permission_data.action,
                scope=permission_data.scope,
                description=permission_data.description,
            )

            self.db.add(permission)
            await self.db.commit()
            await self.db.refresh(permission)

            logger.info(f"Created permission {permission.name}")
            return permission

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating permission: {str(e)}")
            raise

    async def get_permission(self, permission_id: int) -> Optional[Permission]:
        """Get permission by ID.

        Args:
            permission_id: Permission ID

        Returns:
            Permission or None

        Raises:
            Exception: If database operation fails
        """
        try:
            result = await self.db.execute(
                select(Permission).where(Permission.id == permission_id)
            )
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting permission: {str(e)}")
            raise

    async def get_all_permissions(self, skip: int = 0, limit: int = 100) -> Tuple[List[Permission], int]:
        """Get all permissions.

        Args:
            skip: Skip count
            limit: Result limit

        Returns:
            Tuple of permissions and total count

        Raises:
            Exception: If database operation fails
        """
        try:
            count_result = await self.db.execute(select(func.count(Permission.id)))
            total = count_result.scalar() or 0

            result = await self.db.execute(
                select(Permission).order_by(Permission.name).offset(skip).limit(limit)
            )
            permissions = result.scalars().all()

            return permissions, total

        except Exception as e:
            logger.error(f"Error getting permissions: {str(e)}")
            raise


class RoleTemplateService:
    """Service for role template management."""

    def __init__(self, db: AsyncSession):
        """Initialize service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_role_template(self, role_data: RoleTemplateCreate) -> RoleTemplate:
        """Create role template.

        Args:
            role_data: Role template creation data

        Returns:
            Created role template

        Raises:
            Exception: If database operation fails
        """
        try:
            role = RoleTemplate(
                name=role_data.name,
                display_name=role_data.display_name,
                description=role_data.description,
                permissions=role_data.permissions,
                agent_access=role_data.agent_access,
                feature_access=role_data.feature_access,
                is_active=True,
            )

            self.db.add(role)
            await self.db.commit()
            await self.db.refresh(role)

            logger.info(f"Created role template {role.name}")
            return role

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating role template: {str(e)}")
            raise

    async def get_role_template(self, role_id: int) -> Optional[RoleTemplate]:
        """Get role template by ID.

        Args:
            role_id: Role template ID

        Returns:
            Role template or None

        Raises:
            Exception: If database operation fails
        """
        try:
            result = await self.db.execute(
                select(RoleTemplate).where(RoleTemplate.id == role_id)
            )
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting role template: {str(e)}")
            raise

    async def get_all_role_templates(self, skip: int = 0, limit: int = 50) -> Tuple[List[RoleTemplate], int]:
        """Get all role templates.

        Args:
            skip: Skip count
            limit: Result limit

        Returns:
            Tuple of role templates and total count

        Raises:
            Exception: If database operation fails
        """
        try:
            count_result = await self.db.execute(select(func.count(RoleTemplate.id)))
            total = count_result.scalar() or 0

            result = await self.db.execute(
                select(RoleTemplate).where(RoleTemplate.is_active == True).offset(skip).limit(limit)
            )
            roles = result.scalars().all()

            return roles, total

        except Exception as e:
            logger.error(f"Error getting role templates: {str(e)}")
            raise

    async def update_role_template(
        self,
        role_id: int,
        role_data: RoleTemplateUpdate,
    ) -> Optional[RoleTemplate]:
        """Update role template.

        Args:
            role_id: Role template ID
            role_data: Update data

        Returns:
            Updated role template or None

        Raises:
            Exception: If database operation fails
        """
        try:
            role = await self.get_role_template(role_id)
            if not role or role.is_system:
                return role

            if role_data.display_name:
                role.display_name = role_data.display_name
            if role_data.description is not None:
                role.description = role_data.description
            if role_data.permissions is not None:
                role.permissions = role_data.permissions
            if role_data.agent_access is not None:
                role.agent_access = role_data.agent_access
            if role_data.feature_access is not None:
                role.feature_access = role_data.feature_access
            if role_data.is_active is not None:
                role.is_active = role_data.is_active

            await self.db.commit()
            await self.db.refresh(role)

            logger.info(f"Updated role template {role_id}")
            return role

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating role template: {str(e)}")
            raise


class AccessControlService:
    """Service for access control and permission checking."""

    def __init__(self, db: AsyncSession):
        """Initialize service.

        Args:
            db: Database session
        """
        self.db = db

    async def assign_role_to_user(
        self,
        assignment_data: UserRoleAssignmentCreate,
        assigned_by: int,
    ) -> UserRoleAssignment:
        """Assign role to user.

        Args:
            assignment_data: Assignment data
            assigned_by: User ID who made the assignment

        Returns:
            Created assignment

        Raises:
            Exception: If database operation fails
        """
        try:
            assignment = UserRoleAssignment(
                user_id=assignment_data.user_id,
                role_template_id=assignment_data.role_template_id,
                assigned_by=assigned_by,
                expires_at=assignment_data.expires_at,
                is_active=True,
            )

            self.db.add(assignment)
            await self.db.commit()
            await self.db.refresh(assignment)

            logger.info(f"Assigned role {assignment_data.role_template_id} to user {assignment_data.user_id}")
            return assignment

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error assigning role: {str(e)}")
            raise

    async def get_user_roles(self, user_id: int) -> List[RoleTemplate]:
        """Get user's active roles.

        Args:
            user_id: User ID

        Returns:
            List of active role templates

        Raises:
            Exception: If database operation fails
        """
        try:
            result = await self.db.execute(
                select(RoleTemplate).join(
                    UserRoleAssignment,
                    UserRoleAssignment.role_template_id == RoleTemplate.id
                ).where(
                    and_(
                        UserRoleAssignment.user_id == user_id,
                        UserRoleAssignment.is_active == True,
                        or_(
                            UserRoleAssignment.expires_at.is_(None),
                            UserRoleAssignment.expires_at > datetime.utcnow(),
                        ),
                    )
                )
            )
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting user roles: {str(e)}")
            raise

    async def check_permission(
        self,
        user_id: int,
        resource: str,
        action: str,
    ) -> bool:
        """Check if user has permission for resource+action.

        Args:
            user_id: User ID
            resource: Resource name
            action: Action name

        Returns:
            True if user has permission, False otherwise

        Raises:
            Exception: If database operation fails
        """
        try:
            # Get user's roles
            roles = await self.get_user_roles(user_id)

            if not roles:
                logger.warning(f"User {user_id} has no active roles")
                return False

            # Check if any role has the permission
            for role in roles:
                if role.permissions:
                    for perm in role.permissions:
                        if isinstance(perm, dict) and perm.get("resource") == resource and perm.get("action") == action:
                            return True

            logger.debug(f"User {user_id} denied access to {resource}.{action}")
            return False

        except Exception as e:
            logger.error(f"Error checking permission: {str(e)}")
            return False

    async def get_user_agent_permissions(self, user_id: int) -> Dict[str, List[str]]:
        """Get which agents/methods user can access.

        Args:
            user_id: User ID

        Returns:
            Dictionary of {agent_name: [allowed_methods]}

        Raises:
            Exception: If database operation fails
        """
        try:
            roles = await self.get_user_roles(user_id)

            agent_access = {}
            for role in roles:
                if role.agent_access:
                    for agent, methods in role.agent_access.items():
                        if agent not in agent_access:
                            agent_access[agent] = []
                        agent_access[agent].extend(methods)

            return agent_access

        except Exception as e:
            logger.error(f"Error getting user agent permissions: {str(e)}")
            return {}

    async def log_access(
        self,
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
        api_key_id: Optional[int] = None,
    ) -> AccessLog:
        """Log resource access.

        Args:
            user_id: User ID
            resource: Resource accessed
            action: Action performed
            result: Result (allowed/denied)
            ip_address: IP address
            request_path: Request path
            request_method: HTTP method
            entity_id: Optional entity ID
            response_status: HTTP response status
            user_agent: User agent string
            api_key_id: Optional API key ID

        Returns:
            Created access log

        Raises:
            Exception: If database operation fails
        """
        try:
            log = AccessLog(
                user_id=user_id,
                api_key_id=api_key_id,
                resource=resource,
                action=action,
                entity_id=entity_id,
                result=result,
                ip_address=ip_address,
                user_agent=user_agent,
                request_path=request_path,
                request_method=request_method,
                response_status=response_status,
            )

            self.db.add(log)
            await self.db.commit()
            return log

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error logging access: {str(e)}")
            raise


class APIKeyService:
    """Service for API key management."""

    def __init__(self, db: AsyncSession):
        """Initialize service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_api_key(
        self,
        user_id: int,
        key_data: APIKeyCreate,
    ) -> Tuple[str, APIKey]:
        """Create API key.

        Args:
            user_id: User ID
            key_data: API key creation data

        Returns:
            Tuple of (plaintext_key, APIKey_model)

        Raises:
            Exception: If database operation fails
        """
        try:
            # Generate key
            plaintext_key = f"hrp_{secrets.token_urlsafe(32)}"
            key_hash = hashlib.sha256(plaintext_key.encode()).hexdigest()
            key_prefix = plaintext_key[:10]

            # Calculate expiry
            expires_at = None
            if key_data.expires_in_days:
                expires_at = datetime.utcnow() + timedelta(days=key_data.expires_in_days)

            api_key = APIKey(
                user_id=user_id,
                key_hash=key_hash,
                key_prefix=key_prefix,
                name=key_data.name,
                scope=key_data.scope,
                is_active=True,
                expires_at=expires_at,
            )

            self.db.add(api_key)
            await self.db.commit()
            await self.db.refresh(api_key)

            logger.info(f"Created API key {api_key.key_prefix} for user {user_id}")
            return plaintext_key, api_key

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating API key: {str(e)}")
            raise

    async def get_api_keys(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[APIKey], int]:
        """Get user's API keys.

        Args:
            user_id: User ID
            skip: Skip count
            limit: Result limit

        Returns:
            Tuple of API keys and total count

        Raises:
            Exception: If database operation fails
        """
        try:
            count_result = await self.db.execute(
                select(func.count(APIKey.id)).where(APIKey.user_id == user_id)
            )
            total = count_result.scalar() or 0

            result = await self.db.execute(
                select(APIKey)
                .where(APIKey.user_id == user_id)
                .order_by(desc(APIKey.created_at))
                .offset(skip)
                .limit(limit)
            )
            keys = result.scalars().all()

            return keys, total

        except Exception as e:
            logger.error(f"Error getting API keys: {str(e)}")
            raise

    async def verify_api_key(self, plaintext_key: str) -> Optional[APIKey]:
        """Verify API key.

        Args:
            plaintext_key: Plaintext API key

        Returns:
            APIKey model if valid and active, None otherwise

        Raises:
            Exception: If database operation fails
        """
        try:
            key_hash = hashlib.sha256(plaintext_key.encode()).hexdigest()

            result = await self.db.execute(
                select(APIKey).where(
                    and_(
                        APIKey.key_hash == key_hash,
                        APIKey.is_active == True,
                        or_(
                            APIKey.expires_at.is_(None),
                            APIKey.expires_at > datetime.utcnow(),
                        ),
                    )
                )
            )
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error verifying API key: {str(e)}")
            return None

    async def revoke_api_key(self, key_id: int) -> Optional[APIKey]:
        """Revoke API key.

        Args:
            key_id: API key ID

        Returns:
            Updated API key or None

        Raises:
            Exception: If database operation fails
        """
        try:
            result = await self.db.execute(
                select(APIKey).where(APIKey.id == key_id)
            )
            api_key = result.scalar_one_or_none()

            if not api_key:
                return None

            api_key.is_active = False
            api_key.revoked_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(api_key)

            logger.info(f"Revoked API key {api_key.key_prefix}")
            return api_key

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error revoking API key: {str(e)}")
            raise


class SecurityAlertService:
    """Service for security alerts."""

    def __init__(self, db: AsyncSession):
        """Initialize service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_alert(
        self,
        alert_type: str,
        severity: str,
        description: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> SecurityAlert:
        """Create security alert.

        Args:
            alert_type: Type of alert
            severity: Severity level
            description: Alert description
            user_id: Optional user ID
            ip_address: Optional IP address
            details: Optional details

        Returns:
            Created alert

        Raises:
            Exception: If database operation fails
        """
        try:
            alert = SecurityAlert(
                user_id=user_id,
                alert_type=alert_type,
                severity=severity,
                description=description,
                ip_address=ip_address,
                details=details,
                status="open",
            )

            self.db.add(alert)
            await self.db.commit()
            await self.db.refresh(alert)

            logger.warning(f"Created security alert: {alert_type} - {description}")
            return alert

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating security alert: {str(e)}")
            raise

    async def get_open_alerts(self, skip: int = 0, limit: int = 50) -> Tuple[List[SecurityAlert], int]:
        """Get open security alerts.

        Args:
            skip: Skip count
            limit: Result limit

        Returns:
            Tuple of alerts and total count

        Raises:
            Exception: If database operation fails
        """
        try:
            count_result = await self.db.execute(
                select(func.count(SecurityAlert.id)).where(SecurityAlert.status == "open")
            )
            total = count_result.scalar() or 0

            result = await self.db.execute(
                select(SecurityAlert)
                .where(SecurityAlert.status == "open")
                .order_by(desc(SecurityAlert.created_at))
                .offset(skip)
                .limit(limit)
            )
            alerts = result.scalars().all()

            return alerts, total

        except Exception as e:
            logger.error(f"Error getting open alerts: {str(e)}")
            raise

    async def resolve_alert(
        self,
        alert_id: int,
        resolved_by: int,
    ) -> Optional[SecurityAlert]:
        """Resolve security alert.

        Args:
            alert_id: Alert ID
            resolved_by: User ID who resolved

        Returns:
            Updated alert or None

        Raises:
            Exception: If database operation fails
        """
        try:
            result = await self.db.execute(
                select(SecurityAlert).where(SecurityAlert.id == alert_id)
            )
            alert = result.scalar_one_or_none()

            if not alert:
                return None

            alert.status = "resolved"
            alert.resolved_by = resolved_by
            alert.resolved_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(alert)

            logger.info(f"Resolved security alert {alert_id}")
            return alert

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error resolving alert: {str(e)}")
            raise


class SessionPolicyService:
    """Service for session policy management."""

    def __init__(self, db: AsyncSession):
        """Initialize service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_session_policy(self, policy_data: SessionPolicyCreate) -> SessionPolicy:
        """Create session policy.

        Args:
            policy_data: Policy creation data

        Returns:
            Created policy

        Raises:
            Exception: If database operation fails
        """
        try:
            policy = SessionPolicy(
                name=policy_data.name,
                max_session_duration_hours=policy_data.max_session_duration_hours,
                max_concurrent_sessions=policy_data.max_concurrent_sessions,
                idle_timeout_minutes=policy_data.idle_timeout_minutes,
                ip_restriction_enabled=policy_data.ip_restriction_enabled,
                allowed_ips=policy_data.allowed_ips,
                mfa_required=policy_data.mfa_required,
                applies_to_roles=policy_data.applies_to_roles,
                is_active=True,
            )

            self.db.add(policy)
            await self.db.commit()
            await self.db.refresh(policy)

            logger.info(f"Created session policy {policy.name}")
            return policy

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating session policy: {str(e)}")
            raise

    async def get_session_policies(self, skip: int = 0, limit: int = 20) -> Tuple[List[SessionPolicy], int]:
        """Get session policies.

        Args:
            skip: Skip count
            limit: Result limit

        Returns:
            Tuple of policies and total count

        Raises:
            Exception: If database operation fails
        """
        try:
            count_result = await self.db.execute(select(func.count(SessionPolicy.id)))
            total = count_result.scalar() or 0

            result = await self.db.execute(
                select(SessionPolicy)
                .where(SessionPolicy.is_active == True)
                .offset(skip)
                .limit(limit)
            )
            policies = result.scalars().all()

            return policies, total

        except Exception as e:
            logger.error(f"Error getting session policies: {str(e)}")
            raise
