"""Compliance management endpoints for VMS."""

import logging
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.dependencies import get_current_user, get_db, require_role, get_tenant_context_dep
from database.tenant_context import TenantContext
from models.user import User
from models.compliance import ComplianceRequirement, ComplianceRecord, ComplianceScore
from schemas.compliance import (
    ComplianceRequirementCreate, ComplianceRequirementResponse,
    ComplianceRecordCreate, ComplianceRecordUpdate, ComplianceRecordResponse,
    ComplianceScoreResponse, PlacementComplianceResponse
)
from services.compliance_service import ComplianceService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/compliance", tags=["Compliance"])


@router.post("/requirements", response_model=ComplianceRequirementResponse, status_code=status.HTTP_201_CREATED)
async def create_compliance_requirement(
    data: ComplianceRequirementCreate,
    user: User = Depends(require_role("msp_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """Create a compliance requirement."""
    try:
        svc = ComplianceService(db)
        requirement = await svc.create_requirement(data.model_dump())
        return ComplianceRequirementResponse.model_validate(requirement)
    except Exception as e:
        logger.error(f"Error creating compliance requirement: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/requirements", response_model=List[ComplianceRequirementResponse])
async def list_compliance_requirements(
    org_id: Optional[int] = Query(None),
    requirement_type: Optional[str] = Query(None),
    user: User = Depends(require_role("msp_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """List compliance requirements with optional filtering."""
    try:
        query = select(ComplianceRequirement)
        if org_id:
            query = query.where(ComplianceRequirement.organization_id == org_id)
        if requirement_type:
            query = query.where(ComplianceRequirement.requirement_type == requirement_type)

        result = await db.execute(query)
        requirements = result.scalars().all()
        return [ComplianceRequirementResponse.model_validate(r) for r in requirements]
    except Exception as e:
        logger.error(f"Error listing requirements: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/records", response_model=ComplianceRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_compliance_record(
    data: ComplianceRecordCreate,
    user: User = Depends(require_role("msp_admin", "client_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """Create a compliance record for a placement."""
    try:
        svc = ComplianceService(db)
        record = await svc.create_record(data.model_dump())
        return ComplianceRecordResponse.model_validate(record)
    except Exception as e:
        logger.error(f"Error creating compliance record: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/records/{record_id}", response_model=ComplianceRecordResponse)
async def update_compliance_record(
    record_id: int,
    update_data: ComplianceRecordUpdate,
    user: User = Depends(require_role("msp_admin", "client_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """Update compliance record status."""
    try:
        svc = ComplianceService(db)
        record = await svc.update_record_status(
            record_id=record_id,
            status=update_data.status if update_data.status else None,
            verified_by=user.id,
            notes=update_data.verification_notes,
        )
        return ComplianceRecordResponse.model_validate(record)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating compliance record: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/placement/{placement_id}", response_model=PlacementComplianceResponse)
async def check_placement_compliance(
    placement_id: int,
    user: User = Depends(require_role("msp_admin", "client_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """Check compliance status for a placement."""
    try:
        svc = ComplianceService(db)
        is_compliant, details = await svc.check_placement_compliance(placement_id)
        return PlacementComplianceResponse(
            placement_id=placement_id,
            is_compliant=is_compliant,
            **details
        )
    except Exception as e:
        logger.error(f"Error checking placement compliance: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/supplier/{supplier_org_id}/score", response_model=ComplianceScoreResponse)
async def get_supplier_compliance_score(
    supplier_org_id: int,
    user: User = Depends(require_role("msp_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """Get compliance score for a supplier."""
    try:
        svc = ComplianceService(db)
        score_dict = await svc.calculate_supplier_compliance_score(supplier_org_id)
        return ComplianceScoreResponse(**score_dict)
    except Exception as e:
        logger.error(f"Error getting supplier compliance score: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/expiring", response_model=List[ComplianceRecordResponse])
async def get_expiring_compliance(
    days: int = Query(30, ge=1, le=365),
    user: User = Depends(require_role("msp_admin", "client_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """Get compliance items expiring in the next N days."""
    try:
        svc = ComplianceService(db)
        records = await svc.get_expiring_compliance(days_ahead=days)
        return [ComplianceRecordResponse.model_validate(r) for r in records]
    except Exception as e:
        logger.error(f"Error getting expiring compliance: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
