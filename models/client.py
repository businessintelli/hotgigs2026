from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, Date, JSON, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel


class Client(BaseModel):
    """Client/Customer model with enriched fields."""

    __tablename__ = "clients"

    customer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("customers.id"), unique=True, nullable=True)
    company_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    company_size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # startup/small/medium/large/enterprise
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    account_manager_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    client_tier: Mapped[str] = mapped_column(String(50), default="standard")  # standard/premium/enterprise/strategic
    engagement_status: Mapped[str] = mapped_column(String(50), default="active")  # prospect/active/inactive/churned
    health_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-100
    annual_revenue_target: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_revenue_ytd: Mapped[float] = mapped_column(Float, default=0.0)
    payment_terms: Mapped[str] = mapped_column(String(50), default="net_30")  # net_15/net_30/net_45/net_60
    billing_rate_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # hourly/fixed/retainer
    sla_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    onboarded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_interaction_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    contract_start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    contract_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    preferences: Mapped[dict] = mapped_column(JSON, default=dict)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    contacts = relationship("ClientContact", back_populates="client", cascade="all, delete-orphan")
    interactions = relationship("ClientInteraction", back_populates="client", cascade="all, delete-orphan")
    billing = relationship("ClientBilling", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Client(id={self.id}, company_name={self.company_name}, status={self.engagement_status})>"


class ClientContact(BaseModel):
    """Client contact persons."""

    __tablename__ = "client_contacts"

    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    role_type: Mapped[str] = mapped_column(String(50), nullable=False)  # hiring_manager/procurement/hr/executive/technical_lead
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    is_decision_maker: Mapped[bool] = mapped_column(Boolean, default=False)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_contacted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    client = relationship("Client", back_populates="contacts")

    def __repr__(self) -> str:
        return f"<ClientContact(id={self.id}, name={self.first_name} {self.last_name}, role={self.role_type})>"


class ClientInteraction(BaseModel):
    """Client interaction tracking."""

    __tablename__ = "client_interactions"

    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    contact_id: Mapped[Optional[int]] = mapped_column(ForeignKey("client_contacts.id"), nullable=True)
    interaction_type: Mapped[str] = mapped_column(String(50), nullable=False)  # call/email/meeting/qbr/site_visit/other
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    outcome: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # positive/neutral/negative
    follow_up_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    follow_up_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recorded_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    interaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    client = relationship("Client", back_populates="interactions")

    def __repr__(self) -> str:
        return f"<ClientInteraction(id={self.id}, type={self.interaction_type}, client_id={self.client_id})>"


class ClientBilling(BaseModel):
    """Client billing records."""

    __tablename__ = "client_billing"

    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    placement_id: Mapped[Optional[int]] = mapped_column(ForeignKey("offers.id"), nullable=True)
    invoice_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    billing_period_start: Mapped[date] = mapped_column(Date, nullable=False)
    billing_period_end: Mapped[date] = mapped_column(Date, nullable=False)
    hours_billed: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bill_rate: Mapped[float] = mapped_column(Float, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending/invoiced/paid/overdue/disputed
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    client = relationship("Client", back_populates="billing")

    def __repr__(self) -> str:
        return f"<ClientBilling(invoice={self.invoice_number}, amount={self.total_amount}, status={self.status})>"
