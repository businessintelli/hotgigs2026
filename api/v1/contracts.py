import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user
from agents.contract_management_agent import ContractManagementAgent
from services.contract_service import ContractService
from schemas.contract import (
    ContractSchema,
    ContractCreateSchema,
    ContractUpdateSchema,
    ContractFromTemplateSchema,
    ContractSendForSignatureSchema,
    ContractVoidSchema,
    ContractRenewSchema,
    ContractDetailSchema,
    ContractAnalyticsSchema,
)
from schemas.common import PaginatedResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contracts", tags=["contracts"])
agent = ContractManagementAgent()


@router.post("", response_model=ContractSchema, status_code=201)
async def create_contract(
    contract_data: ContractCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ContractSchema:
    """Create a new contract."""
    try:
        contract = await agent.create_contract(
            db, contract_data.dict(), current_user["id"]
        )
        return ContractSchema.from_orm(contract)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating contract: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/from-template", response_model=ContractSchema, status_code=201)
async def create_from_template(
    template_data: ContractFromTemplateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ContractSchema:
    """Create contract from template."""
    try:
        # Generate content from template
        content = await agent.generate_from_template(
            db, template_data.template_type, template_data.context, current_user["id"]
        )

        # Create contract with generated content
        contract_dict = template_data.dict()
        contract_dict["content"] = content
        contract_dict.pop("context", None)

        contract = await agent.create_contract(
            db, contract_dict, current_user["id"]
        )
        return ContractSchema.from_orm(contract)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating contract from template: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("", response_model=PaginatedResponse[ContractSchema])
async def list_contracts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    contract_type: Optional[str] = None,
    candidate_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> PaginatedResponse[ContractSchema]:
    """List contracts with filtering."""
    try:
        contracts, total = await ContractService.list_contracts(
            db,
            skip=skip,
            limit=limit,
            status=status,
            contract_type=contract_type,
            candidate_id=candidate_id,
        )

        return PaginatedResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=contracts,
        )
    except Exception as e:
        logger.error(f"Error listing contracts: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{contract_id}", response_model=ContractDetailSchema)
async def get_contract(
    contract_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ContractDetailSchema:
    """Get full contract details including signatures."""
    try:
        contract = await ContractService.get_contract(db, contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        return contract
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting contract: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{contract_id}", response_model=ContractSchema)
async def update_contract(
    contract_id: int,
    update_data: ContractUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ContractSchema:
    """Update a draft contract."""
    try:
        contract = await ContractService.update_contract(db, contract_id, update_data)
        return contract
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating contract: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{contract_id}/send", response_model=dict)
async def send_for_signature(
    contract_id: int,
    send_data: ContractSendForSignatureSchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Send contract to signers."""
    try:
        result = await agent.send_for_signature(
            db,
            contract_id,
            [s.dict() for s in send_data.signers],
            current_user["id"],
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error sending contract for signature: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{contract_id}/sign", response_model=dict)
async def process_signature(
    contract_id: int,
    token: str = Query(...),
    signature_data: dict = None,
    signer_ip: Optional[str] = None,
) -> dict:
    """Process signature submission (public endpoint)."""
    try:
        # In production, would validate token and get DB session
        return {"status": "signed", "contract_id": contract_id}
    except Exception as e:
        logger.error(f"Error processing signature: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{contract_id}/void", response_model=ContractSchema)
async def void_contract(
    contract_id: int,
    void_data: ContractVoidSchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ContractSchema:
    """Void/cancel a contract."""
    try:
        contract = await agent.void_contract(
            db, contract_id, void_data.reason, current_user["id"]
        )
        return ContractSchema.from_orm(contract)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error voiding contract: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{contract_id}/renew", response_model=ContractSchema, status_code=201)
async def renew_contract(
    contract_id: int,
    renew_data: ContractRenewSchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ContractSchema:
    """Renew a contract."""
    try:
        contract = await agent.renew_contract(
            db, contract_id, renew_data.new_terms, current_user["id"]
        )
        return ContractSchema.from_orm(contract)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error renewing contract: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{contract_id}/audit-trail", response_model=List[dict])
async def get_audit_trail(
    contract_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> List[dict]:
    """Get audit trail for contract."""
    try:
        trail = await ContractService.get_audit_trail(db, contract_id)
        return trail
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting audit trail: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{contract_id}/signing-status", response_model=dict)
async def get_signing_status(
    contract_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Get signing status for contract."""
    try:
        status = await ContractService.get_signing_status(db, contract_id)
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting signing status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{contract_id}/remind", response_model=dict)
async def send_reminders(
    contract_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Send reminders to pending signers."""
    try:
        # In production, would send email reminders
        return {"status": "reminders_sent", "contract_id": contract_id}
    except Exception as e:
        logger.error(f"Error sending reminders: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/expiring", response_model=List[ContractSchema])
async def get_expiring_contracts(
    days_ahead: int = Query(30, ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> List[ContractSchema]:
    """Get contracts expiring within specified days."""
    try:
        contracts = await ContractService.get_expiring_contracts(db, days_ahead)
        return contracts
    except Exception as e:
        logger.error(f"Error getting expiring contracts: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analytics", response_model=ContractAnalyticsSchema)
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ContractAnalyticsSchema:
    """Get contract analytics."""
    try:
        analytics = await agent.get_contract_analytics(db)
        return analytics
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/templates", response_model=List[dict])
async def get_templates(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> List[dict]:
    """List available contract templates."""
    try:
        templates = await ContractService.get_templates(db)
        return templates
    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/verify/{signature_id}", response_model=dict)
async def verify_signature(
    signature_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Verify signature (public endpoint)."""
    try:
        # Placeholder: would verify signature authenticity
        return {"verified": True, "signature_id": signature_id}
    except Exception as e:
        logger.error(f"Error verifying signature: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
