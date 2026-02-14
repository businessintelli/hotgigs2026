import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.client import Client, ClientContact, ClientInteraction, ClientBilling
from agents.client_management_agent import ClientManagementAgent

logger = logging.getLogger(__name__)


class ClientService:
    """Service layer for client operations."""

    def __init__(self):
        """Initialize client service."""
        self.agent = ClientManagementAgent()

    async def initialize(self) -> None:
        """Initialize the service."""
        await self.agent.initialize()

    async def shutdown(self) -> None:
        """Shutdown the service."""
        await self.agent.shutdown()

    # ── Client Management ──

    async def onboard_client(
        self, db: Session, client_data: Dict[str, Any], user_id: int
    ) -> Dict[str, Any]:
        """Onboard a new client."""
        return await self.agent.onboard_client(db, client_data, user_id)

    async def get_client(self, db: Session, client_id: int) -> Optional[Dict[str, Any]]:
        """Get client details."""
        try:
            client = db.execute(select(Client).where(Client.id == client_id)).scalar()

            if not client:
                return None

            contacts = db.execute(
                select(ClientContact).where(ClientContact.client_id == client_id)
            ).scalars().all()

            return {
                "id": client.id,
                "company_name": client.company_name,
                "industry": client.industry,
                "company_size": client.company_size,
                "website": client.website,
                "logo_url": client.logo_url,
                "description": client.description,
                "account_manager_id": client.account_manager_id,
                "client_tier": client.client_tier,
                "engagement_status": client.engagement_status,
                "health_score": client.health_score,
                "annual_revenue_target": client.annual_revenue_target,
                "actual_revenue_ytd": client.actual_revenue_ytd,
                "payment_terms": client.payment_terms,
                "billing_rate_type": client.billing_rate_type,
                "sla_config": client.sla_config,
                "onboarded_at": client.onboarded_at.isoformat() if client.onboarded_at else None,
                "last_interaction_at": client.last_interaction_at.isoformat() if client.last_interaction_at else None,
                "contract_start_date": client.contract_start_date.isoformat() if client.contract_start_date else None,
                "contract_end_date": client.contract_end_date.isoformat() if client.contract_end_date else None,
                "contact_count": len(contacts),
                "created_at": client.created_at.isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting client: {str(e)}")
            return None

    async def list_clients(
        self, db: Session, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """List all clients."""
        return await self.agent.list_clients(db, filters)

    async def update_client(
        self, db: Session, client_id: int, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update client profile."""
        return await self.agent.update_client_profile(db, client_id, updates)

    # ── Contacts ──

    async def add_contact(
        self, db: Session, client_id: int, contact_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add client contact."""
        return await self.agent.add_client_contact(db, client_id, contact_data)

    async def get_contacts(self, db: Session, client_id: int) -> List[Dict[str, Any]]:
        """Get client contacts."""
        try:
            contacts = db.execute(
                select(ClientContact).where(ClientContact.client_id == client_id)
            ).scalars().all()

            return [
                {
                    "id": c.id,
                    "first_name": c.first_name,
                    "last_name": c.last_name,
                    "email": c.email,
                    "phone": c.phone,
                    "title": c.title,
                    "department": c.department,
                    "role_type": c.role_type,
                    "is_primary": c.is_primary,
                    "is_decision_maker": c.is_decision_maker,
                    "last_contacted_at": c.last_contacted_at.isoformat() if c.last_contacted_at else None,
                }
                for c in contacts
            ]
        except Exception as e:
            logger.error(f"Error getting contacts: {str(e)}")
            return []

    async def update_contact(
        self, db: Session, contact_id: int, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update client contact."""
        try:
            contact = db.execute(
                select(ClientContact).where(ClientContact.id == contact_id)
            ).scalar()

            if not contact:
                raise ValueError(f"Contact {contact_id} not found")

            for key, value in updates.items():
                if hasattr(contact, key):
                    setattr(contact, key, value)

            db.commit()
            db.refresh(contact)

            return {
                "id": contact.id,
                "first_name": contact.first_name,
                "last_name": contact.last_name,
                "email": contact.email,
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating contact: {str(e)}")
            raise

    # ── Interactions ──

    async def log_interaction(
        self, db: Session, client_id: int, interaction_data: Dict[str, Any], user_id: int
    ) -> Dict[str, Any]:
        """Log client interaction."""
        try:
            client = db.execute(select(Client).where(Client.id == client_id)).scalar()

            if not client:
                raise ValueError(f"Client {client_id} not found")

            interaction = ClientInteraction(
                client_id=client_id,
                contact_id=interaction_data.get("contact_id"),
                interaction_type=interaction_data["interaction_type"],
                subject=interaction_data["subject"],
                notes=interaction_data.get("notes"),
                outcome=interaction_data.get("outcome"),
                follow_up_date=interaction_data.get("follow_up_date"),
                follow_up_notes=interaction_data.get("follow_up_notes"),
                recorded_by=user_id,
            )

            db.add(interaction)

            # Update client's last interaction
            client.last_interaction_at = datetime.utcnow()

            db.commit()
            db.refresh(interaction)

            logger.info(f"Logged interaction for client {client.company_name}")

            return {
                "id": interaction.id,
                "interaction_type": interaction.interaction_type,
                "subject": interaction.subject,
                "outcome": interaction.outcome,
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error logging interaction: {str(e)}")
            raise

    async def get_interactions(
        self, db: Session, client_id: int, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get client interaction history."""
        try:
            interactions = db.execute(
                select(ClientInteraction)
                .where(ClientInteraction.client_id == client_id)
                .order_by(ClientInteraction.interaction_date.desc())
                .limit(limit)
            ).scalars().all()

            return [
                {
                    "id": i.id,
                    "interaction_type": i.interaction_type,
                    "subject": i.subject,
                    "outcome": i.outcome,
                    "interaction_date": i.interaction_date.isoformat(),
                    "follow_up_date": i.follow_up_date.isoformat() if i.follow_up_date else None,
                }
                for i in interactions
            ]
        except Exception as e:
            logger.error(f"Error getting interactions: {str(e)}")
            return []

    # ── Engagement ──

    async def get_engagement(self, db: Session, client_id: int) -> Dict[str, Any]:
        """Get client engagement metrics."""
        return await self.agent.manage_engagement(db, client_id)

    async def get_health_score(self, db: Session, client_id: int) -> Dict[str, Any]:
        """Get client health score."""
        return await self.agent.get_client_health_score(db, client_id)

    # ── Reporting ──

    async def generate_report(
        self, db: Session, client_id: int, start_date: str, end_date: str
    ) -> Dict[str, Any]:
        """Generate client report."""
        return await self.agent.generate_client_report(db, client_id, start_date, end_date)

    async def generate_qbr(
        self, db: Session, client_id: int, quarter: str
    ) -> Dict[str, Any]:
        """Generate QBR report."""
        return await self.agent.generate_qbr(db, client_id, quarter)

    # ── Billing ──

    async def get_billing_summary(self, db: Session, client_id: int) -> Dict[str, Any]:
        """Get billing summary."""
        return await self.agent.manage_billing(db, client_id)

    async def create_billing_record(
        self, db: Session, client_id: int, billing_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create billing record."""
        try:
            client = db.execute(select(Client).where(Client.id == client_id)).scalar()

            if not client:
                raise ValueError(f"Client {client_id} not found")

            billing = ClientBilling(
                client_id=client_id,
                placement_id=billing_data.get("placement_id"),
                invoice_number=billing_data.get("invoice_number"),
                billing_period_start=billing_data["billing_period_start"],
                billing_period_end=billing_data["billing_period_end"],
                hours_billed=billing_data.get("hours_billed"),
                bill_rate=billing_data["bill_rate"],
                total_amount=billing_data["total_amount"],
                status=billing_data.get("status", "pending"),
                due_date=billing_data.get("due_date"),
                notes=billing_data.get("notes"),
            )

            db.add(billing)

            # Update client revenue
            if billing_data.get("status") == "paid":
                client.actual_revenue_ytd += billing_data["total_amount"]

            db.commit()
            db.refresh(billing)

            logger.info(f"Created billing record for client {client.company_name}")

            return {
                "id": billing.id,
                "invoice_number": billing.invoice_number,
                "total_amount": billing.total_amount,
                "status": billing.status,
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating billing record: {str(e)}")
            raise

    async def get_billing_records(
        self, db: Session, client_id: int
    ) -> List[Dict[str, Any]]:
        """Get client billing records."""
        try:
            records = db.execute(
                select(ClientBilling).where(ClientBilling.client_id == client_id)
            ).scalars().all()

            return [
                {
                    "id": r.id,
                    "invoice_number": r.invoice_number,
                    "billing_period_start": r.billing_period_start.isoformat(),
                    "billing_period_end": r.billing_period_end.isoformat(),
                    "total_amount": r.total_amount,
                    "status": r.status,
                    "due_date": r.due_date.isoformat() if r.due_date else None,
                }
                for r in records
            ]
        except Exception as e:
            logger.error(f"Error getting billing records: {str(e)}")
            return []

    # ── SLA ──

    async def manage_sla(
        self, db: Session, client_id: int, sla_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Manage client SLA."""
        return await self.agent.manage_sla(db, client_id, sla_config)

    # ── Risk Detection ──

    async def get_churn_risk_clients(self, db: Session) -> List[Dict[str, Any]]:
        """Get clients at churn risk."""
        return await self.agent.detect_churn_risk(db)

    # ── Analytics ──

    async def get_analytics(self, db: Session) -> Dict[str, Any]:
        """Get overall client analytics."""
        return await self.agent.get_client_analytics(db)
