"""Digital marketing data models."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, DateTime, Boolean, Float, Text, JSON, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel


class MarketingCampaign(BaseModel):
    """Marketing campaign for jobs or candidate bench/hotlist."""

    __tablename__ = "marketing_campaigns"
    __table_args__ = (
        Index("ix_marketing_campaigns_status", "status"),
        Index("ix_marketing_campaigns_campaign_type", "campaign_type"),
        Index("ix_marketing_campaigns_created_by", "created_by"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    campaign_type: Mapped[str] = mapped_column(String(50), nullable=False)  # job_promotion/bench_marketing/hotlist_blast/brand_awareness
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft/active/paused/completed/cancelled
    requirement_ids: Mapped[Optional[List[int]]] = mapped_column(JSON, nullable=True)
    candidate_ids: Mapped[Optional[List[int]]] = mapped_column(JSON, nullable=True)
    hotlist_id: Mapped[Optional[int]] = mapped_column(ForeignKey("hotlists.id"), nullable=True)
    content: Mapped[Dict[str, Any]] = mapped_column(JSON, default={}, nullable=False)
    target_audience: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    channels: Mapped[List[str]] = mapped_column(JSON, default=[], nullable=False)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    budget_total: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    budget_spent: Mapped[float] = mapped_column(Float, default=0.0)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    applications: Mapped[int] = mapped_column(Integer, default=0)
    conversions: Mapped[int] = mapped_column(Integer, default=0)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationships
    distributions: Mapped[List["CampaignDistribution"]] = relationship("CampaignDistribution", back_populates="campaign")
    email_tracking: Mapped[List["EmailCampaignTracking"]] = relationship("EmailCampaignTracking", back_populates="campaign")


class Hotlist(BaseModel):
    """Curated list of available candidates by skill/domain."""

    __tablename__ = "hotlists"
    __table_args__ = (
        Index("ix_hotlists_status", "status"),
        Index("ix_hotlists_skill_category", "skill_category"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    skill_category: Mapped[str] = mapped_column(String(100), nullable=False)
    candidate_ids: Mapped[List[int]] = mapped_column(JSON, default=[], nullable=False)
    is_auto_updated: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_update_criteria: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active")  # active/archived
    shared_with: Mapped[Optional[List[int]]] = mapped_column(JSON, nullable=True)
    last_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationships
    campaigns: Mapped[List["MarketingCampaign"]] = relationship("MarketingCampaign", foreign_keys="MarketingCampaign.hotlist_id", back_populates=None)


class CampaignDistribution(BaseModel):
    """Distribution tracking for a campaign across channels."""

    __tablename__ = "campaign_distributions"
    __table_args__ = (
        Index("ix_campaign_distributions_campaign_id", "campaign_id"),
        Index("ix_campaign_distributions_channel", "channel"),
        Index("ix_campaign_distributions_status", "status"),
    )

    campaign_id: Mapped[int] = mapped_column(ForeignKey("marketing_campaigns.id"), nullable=False)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)  # linkedin/email/indeed/twitter/facebook
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending/sent/delivered/failed
    distributed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    content_used: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    applications: Mapped[int] = mapped_column(Integer, default=0)
    cost: Mapped[float] = mapped_column(Float, default=0.0)

    # Relationships
    campaign: Mapped["MarketingCampaign"] = relationship("MarketingCampaign", back_populates="distributions")


class EmailCampaignTracking(BaseModel):
    """Email delivery and engagement tracking."""

    __tablename__ = "email_campaign_tracking"
    __table_args__ = (
        Index("ix_email_campaign_tracking_campaign_id", "campaign_id"),
        Index("ix_email_campaign_tracking_status", "status"),
        Index("ix_email_campaign_tracking_recipient_email", "recipient_email"),
    )

    campaign_id: Mapped[int] = mapped_column(ForeignKey("marketing_campaigns.id"), nullable=False)
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    recipient_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    recipient_company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="sent")  # sent/delivered/opened/clicked/bounced/unsubscribed
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    clicked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    open_count: Mapped[int] = mapped_column(Integer, default=0)
    click_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    campaign: Mapped["MarketingCampaign"] = relationship("MarketingCampaign", back_populates="email_tracking")
