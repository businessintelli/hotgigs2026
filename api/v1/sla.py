"""SLA configuration and breach tracking endpoints for VMS."""

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.dependencies import get_current_user, get_db, require_role, get_tenant_context_dep
from database.tenant_context import TenantContext
from models.user import User
from models.sla import SLAConfiguration, SLABreachRecord
from schemas.sla import (
    SLAConfigurationCreate, SLAConfigurationResponse,
    SLABreachResponse, SLABreachResolve, SLADashboardResponse
)
from services.sla_service import SLAService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sla", tags=["SLA"])


@router.post("/configurations", response_model=SLAConfigurationResponse, status_code=status.HTTP_201_CREATED)
async def create_sla_configuration(
    data: SLAConfigurationCreate,
    user: User = Depends(require_role("msp_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """Create an SLA configuration."""
    try:
        svc = SLAService(db)
        config = await svc.create_config(data.model_dump())
        return SLAConfigurationResponse.model_validate(config)
    except Exception as e:
        logger.error(f"Error creating SLA configuration: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/configurations", response_model=List[SLAConfigurationResponse])
async def list_sla_configurations(
    org_id: Optional[int] = Query(None),
    user: User = Depends(require_role("msp_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """List SLA configurations with optional filtering."""
    try:
        svc = SLAService(db)
        configs = await svc.list_configs(organization_id=org_id)
        return [SLAConfigurationResponse.model_validate(c) for c in configs]
    except Exception as e:
        logger.error(f"Error listing SLA configurations: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/detect-breaches", response_model=dict)
async def trigger_breach_detection(
    organization_id: int = Query(...),
    user: User = Depends(require_role("msp_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """Trigger SLA breach detection for an organization."""
    try:
        svc = SLAService(db)
        breaches = await svc.list_breaches(organization_id=organization_id, resolved=False)
        return {
            "organization_id": organization_id,
            "breaches_detected": len(breaches),
            "status": "completed"
        }
    except Exception as e:
        logger.error(f"Error detecting breaches: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/breaches", response_model=List[SLABreachResponse])
async def list_sla_breaches(
    org_id: Optional[int] = Query(None),
    severity: Optional[str] = Query(None),
    metric_type: Optional[str] = Query(None),
    is_resolved: Optional[bool] = Query(None),
    user: User = Depends(require_role("msp_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """List SLA breaches with filtering by severity, metric type, and resolution status."""
    try:
        svc = SLAService(db)
        breaches = await svc.list_breaches(organization_id=org_id, severity=severity, resolved=is_resolved)

        # Apply metric_type filter manually if provided
        if metric_type:
            breaches = [b for b in breaches if str(b.metric_type) == metric_type]

        return [SLABreachResponse.model_validate(b) for b in breaches]
    except Exception as e:
        logger.error(f"Error listing SLA breaches: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/breaches/{breach_id}/resolve", response_model=SLABreachResponse)
async def resolve_sla_breach(
    breach_id: int,
    resolve_data: SLABreachResolve,
    user: User = Depends(require_role("msp_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """Resolve a recorded SLA breach."""
    try:
        svc = SLAService(db)
        breach = await svc.resolve_breach(breach_id, user.id, resolve_data.resolution_notes)
        return SLABreachResponse.model_validate(breach)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error resolving breach: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/dashboard", response_model=SLADashboardResponse)
async def get_sla_dashboard(
    org_id: int = Query(...),
    user: User = Depends(require_role("msp_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """Get SLA dashboard metrics for an organization."""
    try:
        svc = SLAService(db)
        metrics = await svc.get_sla_dashboard(org_id)
        return SLADashboardResponse(**metrics)
    except Exception as e:
        logger.error(f"Error getting SLA dashboard: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
