"""Security and RBAC management API endpoints."""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from schemas.security import (
    PermissionCreate,
    PermissionResponse,
    RoleTemplateCreate,
    RoleTemplateUpdate,
    RoleTemplateResponse,
    UserRoleAssignmentCreate,
    UserRoleAssignmentResponse,
    APIKeyCreate,
    APIKeyResponse,
    APIKeyGeneratedResponse,
    AccessLogResponse,
    AccessLogQuery,
    SecurityAlertResponse,
    SecurityAlertUpdate,
    SessionPolicyCreate,
    SessionPolicyUpdate,
    SessionPolicyResponse,
    SecurityDashboard,
    PermissionCheckResponse,
    UserEffectivePermissions,
    SecurityReport,
)
from schemas.common import PaginatedResponse
from services.security_service import (
    PermissionService,
    RoleTemplateService,
    AccessControlService,
    APIKeyService,
    SecurityAlertService,
    SessionPolicyService,
)
from agents.security_agent import SecurityAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/security", tags=["security"])
security_agent = SecurityAgent()


# ===== PERMISSION ENDPOINTS =====


@router.post("/permissions", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission_data: PermissionCreate,
    db: AsyncSession = Depends(get_db),
) -> PermissionResponse:
    """Create permission.

    Args:
        permission_data: Permission creation data
        db: Database session

    Returns:
        Created permission
    """
    try:
        permission = await security_agent.create_permission(db, permission_data)
        return PermissionResponse.from_orm(permission)

    except Exception as e:
        logger.error(f"Error creating permission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create permission",
        )


@router.get("/permissions", response_model=PaginatedResponse)
async def get_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    """Get all permissions.

    Args:
        skip: Skip count
        limit: Result limit
        db: Database session

    Returns:
        Paginated permissions
    """
    try:
        service = PermissionService(db)
        permissions, total = await service.get_all_permissions(skip=skip, limit=limit)

        return PaginatedResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=[PermissionResponse.from_orm(p) for p in permissions],
        )

    except Exception as e:
        logger.error(f"Error getting permissions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get permissions",
        )


# ===== ROLE TEMPLATE ENDPOINTS =====


@router.post("/roles", response_model=RoleTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_role_template(
    role_data: RoleTemplateCreate,
    db: AsyncSession = Depends(get_db),
) -> RoleTemplateResponse:
    """Create role template.

    Args:
        role_data: Role template creation data
        db: Database session

    Returns:
        Created role template
    """
    try:
        role = await security_agent.create_role_template(db, role_data)
        return RoleTemplateResponse.from_orm(role)

    except Exception as e:
        logger.error(f"Error creating role template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create role template",
        )


@router.get("/roles", response_model=PaginatedResponse)
async def get_role_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    """Get role templates.

    Args:
        skip: Skip count
        limit: Result limit
        db: Database session

    Returns:
        Paginated role templates
    """
    try:
        service = RoleTemplateService(db)
        roles, total = await service.get_all_role_templates(skip=skip, limit=limit)

        return PaginatedResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=[RoleTemplateResponse.from_orm(r) for r in roles],
        )

    except Exception as e:
        logger.error(f"Error getting role templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get role templates",
        )


@router.put("/roles/{role_id}", response_model=RoleTemplateResponse)
async def update_role_template(
    role_id: int,
    role_data: RoleTemplateUpdate,
    db: AsyncSession = Depends(get_db),
) -> RoleTemplateResponse:
    """Update role template.

    Args:
        role_id: Role template ID
        role_data: Update data
        db: Database session

    Returns:
        Updated role template
    """
    try:
        role = await security_agent.update_role_template(db, role_id, role_data)

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role template not found",
            )

        return RoleTemplateResponse.from_orm(role)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating role template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update role template",
        )


# ===== USER ROLE ASSIGNMENT ENDPOINTS =====


@router.post("/users/{user_id}/assign-role", response_model=UserRoleAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def assign_role_to_user(
    user_id: int,
    assignment_data: UserRoleAssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Query(...),
) -> UserRoleAssignmentResponse:
    """Assign role to user.

    Args:
        user_id: User ID
        assignment_data: Assignment data
        db: Database session
        current_user_id: Current user making assignment

    Returns:
        Created assignment
    """
    try:
        assignment = await security_agent.assign_role(
            db,
            user_id,
            assignment_data.role_template_id,
            current_user_id,
            assignment_data.expires_at,
        )
        return UserRoleAssignmentResponse.from_orm(assignment)

    except Exception as e:
        logger.error(f"Error assigning role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign role",
        )


# ===== API KEY ENDPOINTS =====


@router.post("/api-keys", response_model=APIKeyGeneratedResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: APIKeyCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Query(...),
) -> APIKeyGeneratedResponse:
    """Create API key.

    Args:
        key_data: API key creation data
        db: Database session
        user_id: User creating key

    Returns:
        API key with plaintext secret
    """
    try:
        plaintext_key, api_key = await security_agent.create_api_key(
            db,
            user_id,
            key_data.name,
            key_data.scope,
            key_data.expires_in_days,
        )

        return APIKeyGeneratedResponse(
            key=plaintext_key,
            key_prefix=api_key.key_prefix,
            name=api_key.name,
            expires_at=api_key.expires_at,
        )

    except Exception as e:
        logger.error(f"Error creating API key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create API key",
        )


@router.get("/api-keys", response_model=PaginatedResponse)
async def get_api_keys(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user_id: int = Query(...),
) -> PaginatedResponse:
    """Get user's API keys.

    Args:
        skip: Skip count
        limit: Result limit
        db: Database session
        user_id: User ID

    Returns:
        Paginated API keys
    """
    try:
        service = APIKeyService(db)
        keys, total = await service.get_api_keys(user_id, skip=skip, limit=limit)

        return PaginatedResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=[APIKeyResponse.from_orm(k) for k in keys],
        )

    except Exception as e:
        logger.error(f"Error getting API keys: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get API keys",
        )


@router.delete("/api-keys/{key_id}", response_model=APIKeyResponse)
async def revoke_api_key(
    key_id: int,
    db: AsyncSession = Depends(get_db),
) -> APIKeyResponse:
    """Revoke API key.

    Args:
        key_id: API key ID
        db: Database session

    Returns:
        Revoked API key
    """
    try:
        api_key = await security_agent.revoke_api_key(db, key_id)

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found",
            )

        return APIKeyResponse.from_orm(api_key)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking API key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke API key",
        )


# ===== SECURITY ALERT ENDPOINTS =====


@router.get("/alerts", response_model=PaginatedResponse)
async def get_security_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    """Get open security alerts.

    Args:
        skip: Skip count
        limit: Result limit
        db: Database session

    Returns:
        Paginated alerts
    """
    try:
        service = SecurityAlertService(db)
        alerts, total = await service.get_open_alerts(skip=skip, limit=limit)

        return PaginatedResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=[SecurityAlertResponse.from_orm(a) for a in alerts],
        )

    except Exception as e:
        logger.error(f"Error getting security alerts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get security alerts",
        )


@router.put("/alerts/{alert_id}/resolve", response_model=SecurityAlertResponse)
async def resolve_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Query(...),
) -> SecurityAlertResponse:
    """Resolve security alert.

    Args:
        alert_id: Alert ID
        db: Database session
        current_user_id: User resolving alert

    Returns:
        Resolved alert
    """
    try:
        service = SecurityAlertService(db)
        alert = await service.resolve_alert(alert_id, current_user_id)

        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found",
            )

        return SecurityAlertResponse.from_orm(alert)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving alert: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resolve alert",
        )


# ===== PERMISSION CHECK ENDPOINTS =====


@router.get("/permissions/check", response_model=PermissionCheckResponse)
async def check_permission(
    user_id: int = Query(...),
    resource: str = Query(...),
    action: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> PermissionCheckResponse:
    """Check if user has permission.

    Args:
        user_id: User ID
        resource: Resource name
        action: Action name
        db: Database session

    Returns:
        Permission check result
    """
    try:
        has_permission = await security_agent.check_permission(db, user_id, resource, action)

        return PermissionCheckResponse(
            user_id=user_id,
            resource=resource,
            action=action,
            has_permission=has_permission,
        )

    except Exception as e:
        logger.error(f"Error checking permission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check permission",
        )


# ===== USER AGENT PERMISSIONS ENDPOINTS =====


@router.get("/users/{user_id}/agent-access", response_model=dict)
async def get_user_agent_access(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get user's agent access map.

    Args:
        user_id: User ID
        db: Database session

    Returns:
        Agent access mapping
    """
    try:
        agent_access = await security_agent.get_agent_permissions(db, user_id)

        return {
            "user_id": user_id,
            "agent_access": agent_access,
        }

    except Exception as e:
        logger.error(f"Error getting agent access: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get agent access",
        )


# ===== SECURITY DASHBOARD ENDPOINTS =====


@router.get("/dashboard", response_model=SecurityDashboard)
async def get_security_dashboard(
    db: AsyncSession = Depends(get_db),
) -> SecurityDashboard:
    """Get security dashboard data.

    Args:
        db: Database session

    Returns:
        Security dashboard
    """
    try:
        dashboard_data = await security_agent.get_security_dashboard(db)
        return SecurityDashboard(**dashboard_data)

    except Exception as e:
        logger.error(f"Error getting security dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get security dashboard",
        )


# ===== SESSION POLICY ENDPOINTS =====


@router.post("/session-policies", response_model=SessionPolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_session_policy(
    policy_data: SessionPolicyCreate,
    db: AsyncSession = Depends(get_db),
) -> SessionPolicyResponse:
    """Create session policy.

    Args:
        policy_data: Policy creation data
        db: Database session

    Returns:
        Created policy
    """
    try:
        policy = await security_agent.create_session_policy(db, policy_data)
        return SessionPolicyResponse.from_orm(policy)

    except Exception as e:
        logger.error(f"Error creating session policy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session policy",
        )


# ===== AUDIT REPORT ENDPOINTS =====


@router.get("/audit-report", response_model=SecurityReport)
async def generate_audit_report(
    period: str = Query("monthly", pattern="^(daily|weekly|monthly)$"),
    db: AsyncSession = Depends(get_db),
) -> SecurityReport:
    """Generate security audit report.

    Args:
        period: Report period
        db: Database session

    Returns:
        Security report
    """
    try:
        report_data = await security_agent.generate_security_report(db, period)
        return SecurityReport(**report_data)

    except Exception as e:
        logger.error(f"Error generating audit report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate audit report",
        )
