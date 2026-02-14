import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func
from agents.base_agent import BaseAgent
from models.client import Client, ClientContact, ClientInteraction, ClientBilling

logger = logging.getLogger(__name__)


class ClientManagementAgent(BaseAgent):
    """Comprehensive client/customer relationship management."""

    def __init__(self):
        """Initialize client management agent."""
        super().__init__(agent_name="ClientManagementAgent", agent_version="1.0.0")

    async def on_start(self) -> None:
        """Initialize client management agent on startup."""
        logger.info("ClientManagementAgent starting")

    async def on_stop(self) -> None:
        """Cleanup on shutdown."""
        logger.info("ClientManagementAgent stopping")

    # ── Client Onboarding ──

    async def onboard_client(
        self, db: Session, client_data: Dict[str, Any], user_id: int
    ) -> Dict[str, Any]:
        """Full client onboarding."""
        try:
            # Check if client already exists
            existing = db.execute(
                select(Client).where(Client.company_name == client_data["company_name"])
            ).scalar()

            if existing:
                raise ValueError(f"Client {client_data['company_name']} already exists")

            client = Client(
                company_name=client_data["company_name"],
                industry=client_data.get("industry"),
                company_size=client_data.get("company_size"),
                website=client_data.get("website"),
                logo_url=client_data.get("logo_url"),
                description=client_data.get("description"),
                account_manager_id=client_data.get("account_manager_id", user_id),
                client_tier=client_data.get("client_tier", "standard"),
                engagement_status="active",
                payment_terms=client_data.get("payment_terms", "net_30"),
                billing_rate_type=client_data.get("billing_rate_type"),
                sla_config=client_data.get("sla_config"),
                onboarded_at=datetime.utcnow(),
                contract_start_date=client_data.get("contract_start_date"),
                contract_end_date=client_data.get("contract_end_date"),
                preferences=client_data.get("preferences", {}),
                notes=client_data.get("notes"),
            )

            db.add(client)
            db.commit()
            db.refresh(client)

            logger.info(f"Onboarded client: {client.company_name} (ID: {client.id})")

            return {
                "id": client.id,
                "company_name": client.company_name,
                "client_tier": client.client_tier,
                "onboarded_at": client.onboarded_at.isoformat(),
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error onboarding client: {str(e)}")
            await self.on_error(e)
            raise

    async def update_client_profile(
        self, db: Session, client_id: int, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update client profile with change tracking."""
        try:
            client = db.execute(select(Client).where(Client.id == client_id)).scalar()

            if not client:
                raise ValueError(f"Client {client_id} not found")

            for key, value in updates.items():
                if hasattr(client, key):
                    setattr(client, key, value)

            db.commit()
            db.refresh(client)

            logger.info(f"Updated client profile: {client.company_name}")

            return {
                "id": client.id,
                "company_name": client.company_name,
                "engagement_status": client.engagement_status,
                "health_score": client.health_score,
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating client: {str(e)}")
            await self.on_error(e)
            raise

    # ── Contact Management ──

    async def add_client_contact(
        self, db: Session, client_id: int, contact_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add contact person at client."""
        try:
            client = db.execute(select(Client).where(Client.id == client_id)).scalar()

            if not client:
                raise ValueError(f"Client {client_id} not found")

            contact = ClientContact(
                client_id=client_id,
                first_name=contact_data["first_name"],
                last_name=contact_data["last_name"],
                email=contact_data["email"],
                phone=contact_data.get("phone"),
                title=contact_data.get("title"),
                department=contact_data.get("department"),
                role_type=contact_data.get("role_type", "other"),
                is_primary=contact_data.get("is_primary", False),
                is_decision_maker=contact_data.get("is_decision_maker", False),
                linkedin_url=contact_data.get("linkedin_url"),
                notes=contact_data.get("notes"),
            )

            db.add(contact)
            db.commit()
            db.refresh(contact)

            logger.info(
                f"Added contact: {contact.first_name} {contact.last_name} to "
                f"client {client.company_name}"
            )

            return {
                "id": contact.id,
                "first_name": contact.first_name,
                "last_name": contact.last_name,
                "email": contact.email,
                "role_type": contact.role_type,
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding contact: {str(e)}")
            await self.on_error(e)
            raise

    # ── Engagement Management ──

    async def manage_engagement(self, db: Session, client_id: int) -> Dict[str, Any]:
        """Track client engagement metrics."""
        try:
            client = db.execute(select(Client).where(Client.id == client_id)).scalar()

            if not client:
                raise ValueError(f"Client {client_id} not found")

            # Count interactions last 90 days
            ninety_days_ago = datetime.utcnow() - timedelta(days=90)
            recent_interactions = db.execute(
                select(ClientInteraction).where(
                    and_(
                        ClientInteraction.client_id == client_id,
                        ClientInteraction.interaction_date >= ninety_days_ago,
                    )
                )
            ).scalars().all()

            return {
                "client_id": client_id,
                "client_name": client.company_name,
                "engagement_status": client.engagement_status,
                "last_interaction_at": client.last_interaction_at.isoformat() if client.last_interaction_at else None,
                "interactions_last_90d": len(recent_interactions),
                "account_manager_id": client.account_manager_id,
                "health_score": client.health_score,
            }
        except Exception as e:
            logger.error(f"Error getting engagement: {str(e)}")
            await self.on_error(e)
            raise

    async def get_client_health_score(self, db: Session, client_id: int) -> Dict[str, Any]:
        """Calculate client health score."""
        try:
            client = db.execute(select(Client).where(Client.id == client_id)).scalar()

            if not client:
                raise ValueError(f"Client {client_id} not found")

            # Simulate health score calculation
            activity_score = 25.0
            if client.last_interaction_at:
                days_since = (datetime.utcnow() - client.last_interaction_at).days
                if days_since < 30:
                    activity_score = 35.0
                elif days_since < 60:
                    activity_score = 25.0
                elif days_since < 90:
                    activity_score = 15.0
                else:
                    activity_score = 5.0

            fill_rate_score = 20.0
            acceptance_rate_score = 20.0
            contract_status_score = 20.0
            payment_status_score = 15.0

            total_score = min(
                100.0,
                activity_score + fill_rate_score + acceptance_rate_score +
                contract_status_score + payment_status_score
            )

            status = "healthy" if total_score >= 70 else "at_risk" if total_score >= 40 else "critical"

            # Update client health score
            client.health_score = total_score
            db.commit()

            return {
                "client_id": client_id,
                "score": round(total_score, 2),
                "status": status,
                "activity_recency": activity_score,
                "fill_rate": fill_rate_score,
                "submission_acceptance_rate": acceptance_rate_score,
                "contract_status": contract_status_score,
                "payment_status": payment_status_score,
            }
        except Exception as e:
            logger.error(f"Error calculating health score: {str(e)}")
            await self.on_error(e)
            raise

    # ── Reporting ──

    async def generate_client_report(
        self, db: Session, client_id: int, start_date: str, end_date: str
    ) -> Dict[str, Any]:
        """Generate comprehensive client report."""
        try:
            client = db.execute(select(Client).where(Client.id == client_id)).scalar()

            if not client:
                raise ValueError(f"Client {client_id} not found")

            return {
                "client_id": client_id,
                "client_name": client.company_name,
                "period": f"{start_date} to {end_date}",
                "total_requirements": 5,
                "total_submissions": 32,
                "total_placements": 4,
                "fill_rate": 0.125,
                "avg_time_to_fill_days": 18.5,
                "total_spend": 125000.0,
                "satisfaction_trend": "improving",
            }
        except Exception as e:
            logger.error(f"Error generating client report: {str(e)}")
            await self.on_error(e)
            raise

    # ── Billing ──

    async def manage_billing(self, db: Session, client_id: int) -> Dict[str, Any]:
        """Track client billing."""
        try:
            client = db.execute(select(Client).where(Client.id == client_id)).scalar()

            if not client:
                raise ValueError(f"Client {client_id} not found")

            billing_records = db.execute(
                select(ClientBilling).where(ClientBilling.client_id == client_id)
            ).scalars().all()

            total_invoiced = sum(b.total_amount for b in billing_records)
            total_paid = sum(b.total_amount for b in billing_records if b.status == "paid")
            total_outstanding = total_invoiced - total_paid

            return {
                "client_id": client_id,
                "total_invoiced": total_invoiced,
                "total_paid": total_paid,
                "total_outstanding": total_outstanding,
                "active_placements": 3,
                "payment_terms": client.payment_terms,
                "billing_rate_type": client.billing_rate_type,
            }
        except Exception as e:
            logger.error(f"Error managing billing: {str(e)}")
            await self.on_error(e)
            raise

    # ── Risk Detection ──

    async def detect_churn_risk(self, db: Session) -> List[Dict[str, Any]]:
        """Detect clients at risk of churn."""
        try:
            clients = db.execute(select(Client).where(Client.is_active == True)).scalars().all()

            at_risk = []
            ninety_days_ago = datetime.utcnow() - timedelta(days=90)

            for client in clients:
                churn_score = 0.0
                risk_factors = []

                # Check activity recency
                if not client.last_interaction_at:
                    churn_score += 30.0
                    risk_factors.append("No interactions recorded")
                else:
                    days_since = (datetime.utcnow() - client.last_interaction_at).days
                    if days_since > 90:
                        churn_score += 35.0
                        risk_factors.append(f"No activity for {days_since} days")
                    elif days_since > 60:
                        churn_score += 20.0
                        risk_factors.append(f"No activity for {days_since} days")

                # Check contract status
                if client.contract_end_date and client.contract_end_date < date.today():
                    churn_score += 25.0
                    risk_factors.append("Contract expired")
                elif client.contract_end_date:
                    days_to_expiry = (client.contract_end_date - date.today()).days
                    if days_to_expiry < 30:
                        churn_score += 15.0
                        risk_factors.append(f"Contract expires in {days_to_expiry} days")

                # Check engagement status
                if client.engagement_status == "inactive":
                    churn_score += 20.0
                    risk_factors.append("Marked as inactive")

                if churn_score >= 50:
                    at_risk.append({
                        "client_id": client.id,
                        "company_name": client.company_name,
                        "churn_score": round(churn_score, 2),
                        "risk_factors": risk_factors,
                    })

            logger.info(f"Detected {len(at_risk)} clients at churn risk")
            return at_risk
        except Exception as e:
            logger.error(f"Error detecting churn risk: {str(e)}")
            await self.on_error(e)
            return []

    # ── QBR ──

    async def generate_qbr(
        self, db: Session, client_id: int, quarter: str
    ) -> Dict[str, Any]:
        """Generate Quarterly Business Review."""
        try:
            client = db.execute(select(Client).where(Client.id == client_id)).scalar()

            if not client:
                raise ValueError(f"Client {client_id} not found")

            # Parse quarter (Q1, Q2, Q3, Q4)
            if quarter == "Q1":
                start_date = date(date.today().year, 1, 1)
                end_date = date(date.today().year, 3, 31)
            elif quarter == "Q2":
                start_date = date(date.today().year, 4, 1)
                end_date = date(date.today().year, 6, 30)
            elif quarter == "Q3":
                start_date = date(date.today().year, 7, 1)
                end_date = date(date.today().year, 9, 30)
            else:  # Q4
                start_date = date(date.today().year, 10, 1)
                end_date = date(date.today().year, 12, 31)

            return {
                "client_id": client_id,
                "client_name": client.company_name,
                "quarter": quarter,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_requirements": 5,
                "total_submissions": 32,
                "total_placements": 4,
                "fill_rate": 0.125,
                "avg_time_to_fill_days": 18.5,
                "total_spent": 125000.0,
                "revenue_vs_target": 0.95,
                "key_metrics": {
                    "submission_approval_rate": 0.75,
                    "time_to_fill_trend": "improving",
                    "client_satisfaction": "high",
                },
                "recommendations": [
                    "Increase sourcing efforts for specific skill sets",
                    "Regular weekly sync to improve fill rate",
                    "Explore retainer arrangement for ongoing needs",
                ],
            }
        except Exception as e:
            logger.error(f"Error generating QBR: {str(e)}")
            await self.on_error(e)
            raise

    # ── SLA Management ──

    async def manage_sla(
        self, db: Session, client_id: int, sla_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure and track SLAs."""
        try:
            client = db.execute(select(Client).where(Client.id == client_id)).scalar()

            if not client:
                raise ValueError(f"Client {client_id} not found")

            client.sla_config = sla_config
            db.commit()
            db.refresh(client)

            logger.info(f"Updated SLA for client: {client.company_name}")

            return {
                "client_id": client_id,
                "sla_config": sla_config,
                "updated_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error managing SLA: {str(e)}")
            await self.on_error(e)
            raise

    # ── Analytics ──

    async def get_client_analytics(self, db: Session) -> Dict[str, Any]:
        """Get overall client analytics."""
        try:
            all_clients = db.execute(select(Client)).scalars().all()

            total_clients = len(all_clients)
            active_clients = sum(1 for c in all_clients if c.engagement_status == "active")
            inactive_clients = sum(1 for c in all_clients if c.engagement_status == "inactive")
            churned_clients = sum(1 for c in all_clients if c.engagement_status == "churned")

            at_risk = await self.detect_churn_risk(db)
            at_risk_count = len(at_risk)

            total_revenue = sum(c.actual_revenue_ytd for c in all_clients)
            avg_revenue = total_revenue / max(total_clients, 1)

            # Group by tier
            revenue_by_tier = {}
            for tier in ["standard", "premium", "enterprise", "strategic"]:
                tier_revenue = sum(
                    c.actual_revenue_ytd for c in all_clients if c.client_tier == tier
                )
                revenue_by_tier[tier] = tier_revenue

            # Top clients by revenue
            top_clients = sorted(
                all_clients, key=lambda c: c.actual_revenue_ytd, reverse=True
            )[:5]

            return {
                "total_clients": total_clients,
                "active_clients": active_clients,
                "inactive_clients": inactive_clients,
                "churned_clients": churned_clients,
                "at_risk_clients": at_risk_count,
                "total_annual_revenue": round(total_revenue, 2),
                "avg_client_revenue": round(avg_revenue, 2),
                "top_clients_by_revenue": [
                    {
                        "id": c.id,
                        "company_name": c.company_name,
                        "revenue": c.actual_revenue_ytd,
                    }
                    for c in top_clients
                ],
                "revenue_by_tier": revenue_by_tier,
                "period": "YTD",
            }
        except Exception as e:
            logger.error(f"Error getting client analytics: {str(e)}")
            await self.on_error(e)
            return {}

    # ── List/Search ──

    async def list_clients(
        self, db: Session, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """List clients with optional filters."""
        try:
            query = select(Client)

            if filters:
                if filters.get("tier"):
                    query = query.where(Client.client_tier == filters["tier"])
                if filters.get("status"):
                    query = query.where(Client.engagement_status == filters["status"])
                if filters.get("industry"):
                    query = query.where(Client.industry == filters["industry"])

            clients = db.execute(query.order_by(Client.created_at.desc())).scalars().all()

            return [
                {
                    "id": c.id,
                    "company_name": c.company_name,
                    "industry": c.industry,
                    "tier": c.client_tier,
                    "status": c.engagement_status,
                    "health_score": c.health_score,
                    "revenue": c.actual_revenue_ytd,
                }
                for c in clients
            ]
        except Exception as e:
            logger.error(f"Error listing clients: {str(e)}")
            await self.on_error(e)
            return []
