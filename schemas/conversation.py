"""Pydantic schemas for conversational AI interface."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from schemas.common import BaseResponse


class ConversationMessageCreate(BaseModel):
    """Create conversation message."""

    content: str = Field(..., min_length=1, max_length=10000)
    metadata: Optional[Dict[str, Any]] = None


class ConversationMessageResponse(BaseResponse):
    """Conversation message response."""

    conversation_id: int
    role: str  # user/assistant/system/tool
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tokens_used: int = 0
    processing_time_ms: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    """Create new conversation."""

    user_role: str = Field(..., min_length=1, max_length=50)
    title: Optional[str] = Field(None, max_length=255)
    context: Optional[Dict[str, Any]] = None


class ConversationUpdate(BaseModel):
    """Update conversation."""

    title: Optional[str] = Field(None, max_length=255)
    status: Optional[str] = Field(None, max_length=50)
    context: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseResponse):
    """Conversation response."""

    user_id: int
    user_role: str
    title: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    status: str
    message_count: int
    total_tokens: int
    last_message_at: Optional[datetime] = None
    messages: List[ConversationMessageResponse] = []

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """List of conversations."""

    total: int
    conversations: List[ConversationResponse]


class SuggestedPrompt(BaseModel):
    """Suggested prompt/action for user role."""

    title: str
    description: str
    prompt_text: str
    icon: Optional[str] = None
    category: str


class SuggestedPromptsResponse(BaseModel):
    """Suggested prompts for role."""

    role: str
    prompts: List[SuggestedPrompt]


class ConversationSummary(BaseModel):
    """Conversation summary."""

    conversation_id: int
    title: str
    summary: str
    key_topics: List[str]
    action_items: List[str]
    generated_at: datetime


class ToolDefinition(BaseModel):
    """Available tool for conversation."""

    name: str
    description: str
    parameters: Dict[str, Any]
    required_params: List[str]
    return_type: str


class RoleToolsResponse(BaseModel):
    """Available tools for a role."""

    role: str
    available_tools: List[ToolDefinition]
    available_features: List[str]


class ConversationStatistics(BaseModel):
    """Statistics for conversations."""

    total_conversations: int
    active_conversations: int
    archived_conversations: int
    total_messages: int
    average_messages_per_conversation: float
    total_tokens_used: int
    average_tokens_per_conversation: float
    most_common_user_role: str
    average_conversation_duration_hours: float
