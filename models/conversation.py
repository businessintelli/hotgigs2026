"""Conversational AI interface models for role-based chat."""

from datetime import datetime
from typing import Optional, Dict, List, Any
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, JSON, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel


class Conversation(BaseModel):
    """Conversational AI interface for platform users."""

    __tablename__ = "conversations"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    user_role: Mapped[str] = mapped_column(String(50), nullable=False)  # admin/recruiter/manager/candidate/supplier/referrer

    # Conversation metadata
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Auto-generated from first message
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)  # {requirement_id, candidate_id, etc}
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)  # active/archived
    message_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_message_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    messages: "Mapped[List[ConversationMessage]]" = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_conversation_user_status", "user_id", "status"),
        Index("ix_conversation_user_role", "user_id", "user_role"),
        Index("ix_conversation_last_message_at", "last_message_at"),
    )


class ConversationMessage(BaseModel):
    """Individual message in a conversation."""

    __tablename__ = "conversation_messages"

    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"), index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user/assistant/system/tool
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tool_calls: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)  # [{tool_name, params, result}]
    tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    extra_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True)

    # Relationship
    conversation: "Mapped[Conversation]" = relationship("Conversation", back_populates="messages")

    __table_args__ = (
        Index("ix_conversation_message_conversation_id", "conversation_id"),
        Index("ix_conversation_message_role", "role"),
    )
