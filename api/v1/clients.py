import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from services.client_service import ClientService
from schemas.client import (
    ClientCreate, ClientUpdate, ClientResponse,
    ClientContactCreate, ClientContactUpdate, ClientContactResponse,
    ClientInteractionCreate, ClientInteractionResponse,
    ClientBillingCreate, ClientBillingUpdate, ClientBillingResponse,
    ClientHealthScore, ClientBillingSummary, ClientActivityMetrics,
    ClientQBRReport, ChurnRiskClient, ClientAnalytics, SLAConfig,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/clients", tags=["clients"])
client_service = ClientService()


@router.on_event("startup")
async def startup():
    """Initialize client service on startup."""
    await client_service.initialize()


@router.on_event("shutdown")
async def shutdown():
    """Shutdown client service."""
    await client_service.shutdown()


# ── Client Management ──

@router.post("", response_model=Dict[str, Any])
async def onboard_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    current_user_id: int = 1,
):
    """Onboard a new client."""
    try:
        result = await client_service.onboard_client(
            db, client_data.model_dump(), current_user_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error onboarding client: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[Dict[str, Any]])
async def list_clients(
    tier: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List all clients with optional filters."""
    try:
        filters = {}
        if tier:
            filters["tier"] = tier
        if status:
            filters["status"] = status
        if industry:
            filters["industry"] = industry

        clients = await client_service.list_clients(db, filters)
        return clients
    except Exception as e:
        logger.error(f"Error listing clients: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}", response_model=Dict[str, Any])
async def get_client(
    client_id: int,
    db: Session = Depends(get_db),
):
    """Get client full profile."""
    try:
        client = await client_service.get_client(db, client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        return client
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{client_id}", response_model=Dict[str, Any])
async def update_client(
    client_id: int,
    update_data: ClientUpdate,
    db: Session = Depends(get_db),
):
    """Update client profile."""
    try:
        result = await client_service.update_client(
            db, client_id, update_data.model_dump(exclude_unset=True)
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating client: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Contacts ──

@router.post("/{client_id}/contacts", response_model=Dict[str, Any])
async def add_contact(
    client_id: int,
    contact_data: ClientContactCreate,
    db: Session = Depends(get_db),
):
    """Add client contact."""
    try:
        result = await client_service.add_contact(db, client_id, contact_data.model_dump())
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding contact: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}/contacts", response_model=List[Dict[str, Any]])
async def get_contacts(
    client_id: int,
    db: Session = Depends(get_db),
):
    """Get client contacts."""
    try:
        contacts = await client_service.get_contacts(db, client_id)
        return contacts
    except Exception as e:
        logger.error(f"Error getting contacts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{client_id}/contacts/{contact_id}", response_model=Dict[str, Any])
async def update_contact(
    client_id: int,
    contact_id: int,
    update_data: ClientContactUpdate,
    db: Session = Depends(get_db),
):
    """Update client contact."""
    try:
        result = await client_service.update_contact(
            db, contact_id, update_data.model_dump(exclude_unset=True)
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating contact: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Interactions ──

@router.post("/{client_id}/interactions", response_model=Dict[str, Any])
async def log_interaction(
    client_id: int,
    interaction_data: ClientInteractionCreate,
    db: Session = Depends(get_db),
    current_user_id: int = 1,
):
    """Log client interaction."""
    try:
        result = await client_service.log_interaction(
            db, client_id, interaction_data.model_dump(), current_user_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error logging interaction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}/interactions", response_model=List[Dict[str, Any]])
async def get_interactions(
    client_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get client interaction history."""
    try:
        interactions = await client_service.get_interactions(db, client_id, limit)
        return interactions
    except Exception as e:
        logger.error(f"Error getting interactions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Health & Engagement ──

@router.get("/{client_id}/health-score", response_model=Dict[str, Any])
async def get_health_score(
    client_id: int,
    db: Session = Depends(get_db),
):
    """Get client health score."""
    try:
        score = await client_service.get_health_score(db, client_id)
        return score
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting health score: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Reporting ──

@router.get("/{client_id}/report", response_model=Dict[str, Any])
async def generate_report(
    client_id: int,
    start_date: str = Query(...),
    end_date: str = Query(...),
    db: Session = Depends(get_db),
):
    """Generate client report."""
    try:
        report = await client_service.generate_report(db, client_id, start_date, end_date)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{client_id}/qbr", response_model=Dict[str, Any])
async def generate_qbr(
    client_id: int,
    quarter: str = Query(..., pattern="^Q[1-4]$"),
    db: Session = Depends(get_db),
):
    """Generate QBR report."""
    try:
        qbr = await client_service.generate_qbr(db, client_id, quarter)
        return qbr
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating QBR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Billing ──

@router.get("/{client_id}/billing", response_model=Dict[str, Any])
async def get_billing_summary(
    client_id: int,
    db: Session = Depends(get_db),
):
    """Get client billing summary."""
    try:
        summary = await client_service.get_billing_summary(db, client_id)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting billing summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{client_id}/billing", response_model=Dict[str, Any])
async def create_billing_record(
    client_id: int,
    billing_data: ClientBillingCreate,
    db: Session = Depends(get_db),
):
    """Create billing record."""
    try:
        result = await client_service.create_billing_record(
            db, client_id, billing_data.model_dump()
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating billing record: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}/billing/records", response_model=List[Dict[str, Any]])
async def get_billing_records(
    client_id: int,
    db: Session = Depends(get_db),
):
    """Get client billing records."""
    try:
        records = await client_service.get_billing_records(db, client_id)
        return records
    except Exception as e:
        logger.error(f"Error getting billing records: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ── SLA ──

@router.get("/{client_id}/sla", response_model=Dict[str, Any])
async def get_sla(
    client_id: int,
    db: Session = Depends(get_db),
):
    """Get client SLA configuration."""
    try:
        client = await client_service.get_client(db, client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        return {
            "client_id": client_id,
            "sla_config": client.get("sla_config"),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting SLA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{client_id}/sla", response_model=Dict[str, Any])
async def update_sla(
    client_id: int,
    sla_config: SLAConfig,
    db: Session = Depends(get_db),
):
    """Update client SLA configuration."""
    try:
        result = await client_service.manage_sla(db, client_id, sla_config.model_dump())
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating SLA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Risk & Analytics ──

@router.get("/churn-risk", response_model=List[Dict[str, Any]])
async def get_churn_risk_clients(db: Session = Depends(get_db)):
    """Get clients at churn risk."""
    try:
        clients = await client_service.get_churn_risk_clients(db)
        return clients
    except Exception as e:
        logger.error(f"Error getting churn risk clients: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics", response_model=Dict[str, Any])
async def get_analytics(db: Session = Depends(get_db)):
    """Get overall client analytics."""
    try:
        analytics = await client_service.get_analytics(db)
        return analytics
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
