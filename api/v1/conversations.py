"""Conversational AI interface API endpoints."""

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationListResponse,
    ConversationMessageCreate,
    ConversationMessageResponse,
    ConversationSummary,
    SuggestedPromptsResponse,
    RoleToolsResponse,
)
from services.conversation_service import ConversationService
from agents.conversational_interface_agent import ConversationalInterfaceAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversations", tags=["conversations"])
conversation_agent = ConversationalInterfaceAgent()


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Query(...),
) -> ConversationResponse:
    """Start new conversation.

    Args:
        conversation_data: Conversation creation data
        db: Database session
        user_id: User starting conversation

    Returns:
        Created conversation
    """
    try:
        conversation = await conversation_agent.start_conversation(
            db,
            user_id,
            conversation_data.user_role,
            conversation_data.context,
        )
        return ConversationResponse.from_orm(conversation)

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation",
        )


@router.get("", response_model=ConversationListResponse)
async def get_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user_id: int = Query(...),
) -> ConversationListResponse:
    """Get user's conversations.

    Args:
        skip: Skip count
        limit: Result limit
        status: Filter by status
        db: Database session
        user_id: User ID

    Returns:
        List of conversations
    """
    try:
        service = ConversationService(db)
        conversations, total = await service.get_user_conversations(
            user_id,
            skip=skip,
            limit=limit,
            status=status,
        )

        return ConversationListResponse(
            total=total,
            conversations=[ConversationResponse.from_orm(c) for c in conversations],
        )

    except Exception as e:
        logger.error(f"Error getting conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get conversations",
        )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
) -> ConversationResponse:
    """Get conversation with messages.

    Args:
        conversation_id: Conversation ID
        db: Database session

    Returns:
        Conversation with messages
    """
    try:
        service = ConversationService(db)
        conversation = await service.get_conversation(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        # Get messages
        messages, _ = await service.get_conversation_messages(conversation_id, skip=0, limit=50)
        conversation.messages = messages

        return ConversationResponse.from_orm(conversation)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get conversation",
        )


@router.post("/{conversation_id}/message", response_model=ConversationMessageResponse)
async def send_message(
    conversation_id: int,
    message_data: ConversationMessageCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Query(...),
) -> ConversationMessageResponse:
    """Send message to conversation.

    Args:
        conversation_id: Conversation ID
        message_data: Message content
        db: Database session
        user_id: User sending message

    Returns:
        User's message (assistant response would follow separately)
    """
    try:
        message = await conversation_agent.send_message(
            db,
            conversation_id,
            user_id,
            message_data.content,
            message_data.metadata,
        )

        # Generate assistant response
        assistant_message = await conversation_agent.generate_response(
            db,
            conversation_id,
            user_id,
        )

        return ConversationMessageResponse.from_orm(message)

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message",
        )


@router.post("/{conversation_id}/archive", response_model=ConversationResponse)
async def archive_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
) -> ConversationResponse:
    """Archive conversation.

    Args:
        conversation_id: Conversation ID
        db: Database session

    Returns:
        Updated conversation
    """
    try:
        service = ConversationService(db)
        conversation = await service.archive_conversation(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        return ConversationResponse.from_orm(conversation)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error archiving conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to archive conversation",
        )


@router.get("/{conversation_id}/summarize", response_model=ConversationSummary)
async def summarize_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
) -> ConversationSummary:
    """Get conversation summary.

    Args:
        conversation_id: Conversation ID
        db: Database session

    Returns:
        Conversation summary
    """
    try:
        summary_data = await conversation_agent.summarize_conversation(db, conversation_id)
        return ConversationSummary(**summary_data)

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error summarizing conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to summarize conversation",
        )


@router.get("/suggested-prompts", response_model=SuggestedPromptsResponse)
async def get_suggested_prompts(
    user_role: str = Query(..., min_length=1, max_length=50),
) -> SuggestedPromptsResponse:
    """Get suggested prompts for user role.

    Args:
        user_role: User's role

    Returns:
        List of suggested prompts
    """
    try:
        prompts = await conversation_agent.get_suggested_prompts(user_role)
        return SuggestedPromptsResponse(role=user_role, prompts=prompts)

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error getting suggested prompts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get suggested prompts",
        )


@router.get("/role-tools", response_model=RoleToolsResponse)
async def get_role_tools(
    user_role: str = Query(..., min_length=1, max_length=50),
) -> RoleToolsResponse:
    """Get available tools for user role.

    Args:
        user_role: User's role

    Returns:
        Available tools and features
    """
    try:
        tools = await conversation_agent.get_role_tools(user_role)
        features = list(conversation_agent.ROLE_FEATURES.get(user_role, {}).keys())

        return RoleToolsResponse(
            role=user_role,
            available_tools=[
                {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": {},
                    "required_params": [],
                    "return_type": "dict",
                }
                for tool in tools
            ],
            available_features=features,
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error getting role tools: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get role tools",
        )
