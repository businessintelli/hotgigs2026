"""Conversational AI interface service."""

import logging
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from models.conversation import Conversation, ConversationMessage
from schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationMessageCreate,
)

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for conversation CRUD and history management."""

    def __init__(self, db: AsyncSession):
        """Initialize service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_conversation(
        self,
        user_id: int,
        conversation_data: ConversationCreate,
    ) -> Conversation:
        """Create new conversation.

        Args:
            user_id: User ID
            conversation_data: Conversation creation data

        Returns:
            Created conversation

        Raises:
            Exception: If database operation fails
        """
        try:
            conversation = Conversation(
                user_id=user_id,
                user_role=conversation_data.user_role,
                title=conversation_data.title,
                context=conversation_data.context,
                status="active",
            )

            self.db.add(conversation)
            await self.db.commit()
            await self.db.refresh(conversation)

            logger.info(f"Created conversation {conversation.id} for user {user_id}")
            return conversation

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating conversation: {str(e)}")
            raise

    async def get_conversation(self, conversation_id: int) -> Optional[Conversation]:
        """Get conversation by ID.

        Args:
            conversation_id: Conversation ID

        Returns:
            Conversation or None

        Raises:
            Exception: If database operation fails
        """
        try:
            result = await self.db.execute(
                select(Conversation).where(Conversation.id == conversation_id)
            )
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting conversation: {str(e)}")
            raise

    async def get_user_conversations(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
    ) -> Tuple[List[Conversation], int]:
        """Get user's conversations with pagination.

        Args:
            user_id: User ID
            skip: Skip count
            limit: Result limit
            status: Filter by status

        Returns:
            Tuple of conversations and total count

        Raises:
            Exception: If database operation fails
        """
        try:
            query = select(Conversation).where(Conversation.user_id == user_id)
            count_query = select(func.count(Conversation.id)).where(Conversation.user_id == user_id)

            if status:
                query = query.where(Conversation.status == status)
                count_query = count_query.where(Conversation.status == status)

            count_result = await self.db.execute(count_query)
            total = count_result.scalar() or 0

            result = await self.db.execute(
                query.order_by(desc(Conversation.last_message_at)).offset(skip).limit(limit)
            )
            conversations = result.scalars().all()

            return conversations, total

        except Exception as e:
            logger.error(f"Error getting user conversations: {str(e)}")
            raise

    async def update_conversation(
        self,
        conversation_id: int,
        conversation_data: ConversationUpdate,
    ) -> Optional[Conversation]:
        """Update conversation.

        Args:
            conversation_id: Conversation ID
            conversation_data: Update data

        Returns:
            Updated conversation or None

        Raises:
            Exception: If database operation fails
        """
        try:
            conversation = await self.get_conversation(conversation_id)
            if not conversation:
                return None

            if conversation_data.title:
                conversation.title = conversation_data.title
            if conversation_data.status:
                conversation.status = conversation_data.status
            if conversation_data.context:
                conversation.context = conversation_data.context

            await self.db.commit()
            await self.db.refresh(conversation)

            logger.info(f"Updated conversation {conversation_id}")
            return conversation

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating conversation: {str(e)}")
            raise

    async def archive_conversation(self, conversation_id: int) -> Optional[Conversation]:
        """Archive conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            Updated conversation or None

        Raises:
            Exception: If database operation fails
        """
        try:
            conversation = await self.get_conversation(conversation_id)
            if not conversation:
                return None

            conversation.status = "archived"
            await self.db.commit()
            await self.db.refresh(conversation)

            logger.info(f"Archived conversation {conversation_id}")
            return conversation

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error archiving conversation: {str(e)}")
            raise

    async def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        tokens_used: int = 0,
        processing_time_ms: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ConversationMessage:
        """Add message to conversation.

        Args:
            conversation_id: Conversation ID
            role: Message role (user/assistant/system/tool)
            content: Message content
            tool_calls: Optional tool calls made
            tokens_used: Tokens consumed
            processing_time_ms: Processing time in milliseconds
            metadata: Optional metadata

        Returns:
            Created message

        Raises:
            Exception: If database operation fails
        """
        try:
            message = ConversationMessage(
                conversation_id=conversation_id,
                role=role,
                content=content,
                tool_calls=tool_calls,
                tokens_used=tokens_used,
                processing_time_ms=processing_time_ms,
                metadata=metadata or {},
            )

            self.db.add(message)

            # Update conversation
            conversation = await self.get_conversation(conversation_id)
            if conversation:
                conversation.message_count += 1
                conversation.total_tokens += tokens_used
                conversation.last_message_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(message)

            logger.info(f"Added message to conversation {conversation_id}")
            return message

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error adding message: {str(e)}")
            raise

    async def get_conversation_messages(
        self,
        conversation_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[ConversationMessage], int]:
        """Get conversation messages with pagination.

        Args:
            conversation_id: Conversation ID
            skip: Skip count
            limit: Result limit

        Returns:
            Tuple of messages and total count

        Raises:
            Exception: If database operation fails
        """
        try:
            query = select(ConversationMessage).where(
                ConversationMessage.conversation_id == conversation_id
            )
            count_query = select(func.count(ConversationMessage.id)).where(
                ConversationMessage.conversation_id == conversation_id
            )

            count_result = await self.db.execute(count_query)
            total = count_result.scalar() or 0

            result = await self.db.execute(
                query.order_by(ConversationMessage.created_at).offset(skip).limit(limit)
            )
            messages = result.scalars().all()

            return messages, total

        except Exception as e:
            logger.error(f"Error getting conversation messages: {str(e)}")
            raise

    async def get_conversation_history(
        self,
        conversation_id: int,
    ) -> List[ConversationMessage]:
        """Get full conversation history.

        Args:
            conversation_id: Conversation ID

        Returns:
            List of all messages

        Raises:
            Exception: If database operation fails
        """
        try:
            result = await self.db.execute(
                select(ConversationMessage)
                .where(ConversationMessage.conversation_id == conversation_id)
                .order_by(ConversationMessage.created_at)
            )
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            raise

    async def search_conversations(
        self,
        user_id: int,
        search_term: str,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Conversation], int]:
        """Search conversations by title or content.

        Args:
            user_id: User ID
            search_term: Search term
            skip: Skip count
            limit: Result limit

        Returns:
            Tuple of conversations and total count

        Raises:
            Exception: If database operation fails
        """
        try:
            # Search in conversation titles
            query = select(Conversation).where(
                and_(
                    Conversation.user_id == user_id,
                    Conversation.title.ilike(f"%{search_term}%"),
                )
            )
            count_query = select(func.count(Conversation.id)).where(
                and_(
                    Conversation.user_id == user_id,
                    Conversation.title.ilike(f"%{search_term}%"),
                )
            )

            count_result = await self.db.execute(count_query)
            total = count_result.scalar() or 0

            result = await self.db.execute(
                query.order_by(desc(Conversation.last_message_at)).offset(skip).limit(limit)
            )
            conversations = result.scalars().all()

            return conversations, total

        except Exception as e:
            logger.error(f"Error searching conversations: {str(e)}")
            raise

    async def get_conversation_statistics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get conversation statistics.

        Args:
            user_id: Optional user ID for user-specific stats

        Returns:
            Statistics dictionary

        Raises:
            Exception: If database operation fails
        """
        try:
            if user_id:
                result = await self.db.execute(
                    select(Conversation).where(Conversation.user_id == user_id)
                )
            else:
                result = await self.db.execute(select(Conversation))

            conversations = result.scalars().all()

            if not conversations:
                return {
                    "total_conversations": 0,
                    "active_conversations": 0,
                    "archived_conversations": 0,
                    "total_messages": 0,
                    "average_messages_per_conversation": 0,
                    "total_tokens_used": 0,
                    "average_tokens_per_conversation": 0,
                    "user_role_distribution": {},
                }

            total = len(conversations)
            active = len([c for c in conversations if c.status == "active"])
            archived = len([c for c in conversations if c.status == "archived"])

            total_messages = sum(c.message_count for c in conversations)
            total_tokens = sum(c.total_tokens for c in conversations)

            # Role distribution
            role_dist = {}
            for c in conversations:
                role_dist[c.user_role] = role_dist.get(c.user_role, 0) + 1

            return {
                "total_conversations": total,
                "active_conversations": active,
                "archived_conversations": archived,
                "total_messages": total_messages,
                "average_messages_per_conversation": round(total_messages / total, 2) if total > 0 else 0,
                "total_tokens_used": total_tokens,
                "average_tokens_per_conversation": round(total_tokens / total, 2) if total > 0 else 0,
                "user_role_distribution": role_dist,
            }

        except Exception as e:
            logger.error(f"Error getting conversation statistics: {str(e)}")
            raise
