"""AI Copilot conversation and insight models."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, DateTime, JSON, ForeignKey, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel


class CopilotConversation(BaseModel):
    """AI Copilot conversation tracking model."""

    __tablename__ = "copilot_conversations"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    context_requirement_id: Mapped[Optional[int]] = mapped_column(ForeignKey("requirements.id"))
    context_candidate_id: Mapped[Optional[int]] = mapped_column(ForeignKey("candidates.id"))
    context_metadata: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens_used: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    messages = relationship(
        "CopilotMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )
    insights = relationship(
        "CopilotInsight",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<CopilotConversation(id={self.id}, user_id={self.user_id}, title={self.title})>"


class CopilotMessage(BaseModel):
    """AI Copilot conversation message model."""

    __tablename__ = "copilot_messages"

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("copilot_conversations.id"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user/assistant/system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    function_calls: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    function_results: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    extra_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSON, default=dict)

    # Relationships
    conversation = relationship("CopilotConversation", back_populates="messages")

    def __repr__(self) -> str:
        return f"<CopilotMessage(id={self.id}, conversation_id={self.conversation_id}, role={self.role})>"


class CopilotInsight(BaseModel):
    """AI-generated insight from copilot analysis."""

    __tablename__ = "copilot_insights"

    conversation_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("copilot_conversations.id")
    )
    insight_type: Mapped[str] = mapped_column(String(50), nullable=False)  # market/pipeline/candidate/requirement
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(20), default="info")  # info/warning/critical
    entity_type: Mapped[Optional[str]] = mapped_column(String(50))  # candidate/requirement/submission/offer
    entity_id: Mapped[Optional[int]] = mapped_column(Integer)
    recommendations: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    confidence_score: Mapped[Optional[float]] = mapped_column(default=0.0)
    is_read: Mapped[bool] = mapped_column(default=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    extra_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSON, default=dict)

    # Relationships
    conversation = relationship("CopilotConversation", back_populates="insights")

    def __repr__(self) -> str:
        return f"<CopilotInsight(id={self.id}, insight_type={self.insight_type}, severity={self.severity})>"
