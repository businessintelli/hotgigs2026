"""Copilot conversation and insight service."""

import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from models.copilot import CopilotConversation, CopilotMessage, CopilotInsight
from schemas.copilot import (
    CopilotConversationCreate,
    CopilotConversationUpdate,
    CopilotMessageCreate,
    CopilotInsightCreate,
)

logger = logging.getLogger(__name__)


class CopilotConversationService:
    """Service for managing copilot conversations."""

    def __init__(self, db: AsyncSession):
        """Initialize conversation service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_conversation(
        self,
        conversation_data: CopilotConversationCreate,
        user_id: int,
    ) -> CopilotConversation:
        """Create new conversation.

        Args:
            conversation_data: Conversation creation data
            user_id: User ID

        Returns:
            Created conversation

        Raises:
            Exception: If database operation fails
        """
        try:
            conversation = CopilotConversation(
                user_id=user_id,
                **conversation_data.model_dump(),
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

    async def get_conversation(
        self,
        conversation_id: int,
    ) -> Optional[CopilotConversation]:
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
                select(CopilotConversation).where(
                    CopilotConversation.id == conversation_id
                )
            )
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting conversation: {str(e)}")
            raise

    async def get_conversations(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[CopilotConversation], int]:
        """Get user's conversations.

        Args:
            user_id: User ID
            skip: Skip count
            limit: Result limit

        Returns:
            Tuple of conversations and count

        Raises:
            Exception: If database operation fails
        """
        try:
            query = select(CopilotConversation).where(
                CopilotConversation.user_id == user_id
            )
            count_query = select(func.count(CopilotConversation.id)).where(
                CopilotConversation.user_id == user_id
            )

            # Get total
            result = await self.db.execute(count_query)
            total = result.scalar() or 0

            # Get paginated
            result = await self.db.execute(
                query.order_by(desc(CopilotConversation.created_at))
                .offset(skip)
                .limit(limit)
            )
            conversations = result.scalars().all()

            logger.info(f"Retrieved {len(conversations)} conversations for user {user_id}")
            return conversations, total

        except Exception as e:
            logger.error(f"Error getting conversations: {str(e)}")
            raise

    async def update_conversation(
        self,
        conversation_id: int,
        conversation_data: CopilotConversationUpdate,
    ) -> CopilotConversation:
        """Update conversation.

        Args:
            conversation_id: Conversation ID
            conversation_data: Update data

        Returns:
            Updated conversation

        Raises:
            ValueError: If conversation not found
        """
        try:
            result = await self.db.execute(
                select(CopilotConversation).where(
                    CopilotConversation.id == conversation_id
                )
            )
            conversation = result.scalar_one_or_none()

            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")

            # Update fields
            update_data = conversation_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(conversation, field, value)

            self.db.add(conversation)
            await self.db.commit()
            await self.db.refresh(conversation)

            logger.info(f"Updated conversation {conversation_id}")
            return conversation

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating conversation: {str(e)}")
            raise

    async def delete_conversation(self, conversation_id: int) -> bool:
        """Soft delete conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            True if successful

        Raises:
            ValueError: If conversation not found
        """
        try:
            result = await self.db.execute(
                select(CopilotConversation).where(
                    CopilotConversation.id == conversation_id
                )
            )
            conversation = result.scalar_one_or_none()

            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")

            conversation.is_active = False
            self.db.add(conversation)
            await self.db.commit()

            logger.info(f"Deleted conversation {conversation_id}")
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting conversation: {str(e)}")
            raise


class CopilotMessageService:
    """Service for managing copilot messages."""

    def __init__(self, db: AsyncSession):
        """Initialize message service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_message(
        self,
        conversation_id: int,
        message_data: CopilotMessageCreate,
        role: str,
    ) -> CopilotMessage:
        """Create message.

        Args:
            conversation_id: Conversation ID
            message_data: Message creation data
            role: Message role (user/assistant/system)

        Returns:
            Created message

        Raises:
            Exception: If database operation fails
        """
        try:
            message = CopilotMessage(
                conversation_id=conversation_id,
                role=role,
                **message_data.model_dump(),
            )
            self.db.add(message)
            await self.db.commit()
            await self.db.refresh(message)

            logger.info(f"Created message {message.id} in conversation {conversation_id}")
            return message

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating message: {str(e)}")
            raise

    async def get_messages(
        self,
        conversation_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[List[CopilotMessage], int]:
        """Get conversation messages.

        Args:
            conversation_id: Conversation ID
            skip: Skip count
            limit: Result limit

        Returns:
            Tuple of messages and count

        Raises:
            Exception: If database operation fails
        """
        try:
            query = select(CopilotMessage).where(
                CopilotMessage.conversation_id == conversation_id
            )
            count_query = select(func.count(CopilotMessage.id)).where(
                CopilotMessage.conversation_id == conversation_id
            )

            # Get total
            result = await self.db.execute(count_query)
            total = result.scalar() or 0

            # Get paginated (ordered by creation time)
            result = await self.db.execute(
                query.order_by(CopilotMessage.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            messages = list(reversed(result.scalars().all()))

            logger.info(f"Retrieved {len(messages)} messages from conversation {conversation_id}")
            return messages, total

        except Exception as e:
            logger.error(f"Error getting messages: {str(e)}")
            raise

    async def get_message(self, message_id: int) -> Optional[CopilotMessage]:
        """Get message by ID.

        Args:
            message_id: Message ID

        Returns:
            Message or None

        Raises:
            Exception: If database operation fails
        """
        try:
            result = await self.db.execute(
                select(CopilotMessage).where(CopilotMessage.id == message_id)
            )
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting message: {str(e)}")
            raise


class CopilotInsightService:
    """Service for managing copilot insights."""

    def __init__(self, db: AsyncSession):
        """Initialize insight service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_insight(
        self,
        insight_data: CopilotInsightCreate,
        conversation_id: Optional[int] = None,
    ) -> CopilotInsight:
        """Create insight.

        Args:
            insight_data: Insight creation data
            conversation_id: Optional conversation ID

        Returns:
            Created insight

        Raises:
            Exception: If database operation fails
        """
        try:
            insight = CopilotInsight(
                conversation_id=conversation_id,
                **insight_data.model_dump(),
            )
            self.db.add(insight)
            await self.db.commit()
            await self.db.refresh(insight)

            logger.info(f"Created {insight.insight_type} insight {insight.id}")
            return insight

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating insight: {str(e)}")
            raise

    async def get_insight(self, insight_id: int) -> Optional[CopilotInsight]:
        """Get insight by ID.

        Args:
            insight_id: Insight ID

        Returns:
            Insight or None

        Raises:
            Exception: If database operation fails
        """
        try:
            result = await self.db.execute(
                select(CopilotInsight).where(CopilotInsight.id == insight_id)
            )
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting insight: {str(e)}")
            raise

    async def get_insights(
        self,
        conversation_id: Optional[int] = None,
        insight_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[CopilotInsight], int]:
        """Get insights with filtering.

        Args:
            conversation_id: Filter by conversation
            insight_type: Filter by type
            entity_id: Filter by entity
            skip: Skip count
            limit: Result limit

        Returns:
            Tuple of insights and count

        Raises:
            Exception: If database operation fails
        """
        try:
            query = select(CopilotInsight)
            count_query = select(func.count(CopilotInsight.id))

            # Apply filters
            filters = []
            if conversation_id:
                filters.append(CopilotInsight.conversation_id == conversation_id)
            if insight_type:
                filters.append(CopilotInsight.insight_type == insight_type)
            if entity_id:
                filters.append(CopilotInsight.entity_id == entity_id)

            if filters:
                query = query.where(and_(*filters))
                count_query = count_query.where(and_(*filters))

            # Get total
            result = await self.db.execute(count_query)
            total = result.scalar() or 0

            # Get paginated
            result = await self.db.execute(
                query.order_by(desc(CopilotInsight.created_at))
                .offset(skip)
                .limit(limit)
            )
            insights = result.scalars().all()

            logger.info(f"Retrieved {len(insights)} insights")
            return insights, total

        except Exception as e:
            logger.error(f"Error getting insights: {str(e)}")
            raise

    async def mark_insight_read(self, insight_id: int) -> CopilotInsight:
        """Mark insight as read.

        Args:
            insight_id: Insight ID

        Returns:
            Updated insight

        Raises:
            ValueError: If insight not found
        """
        try:
            result = await self.db.execute(
                select(CopilotInsight).where(CopilotInsight.id == insight_id)
            )
            insight = result.scalar_one_or_none()

            if not insight:
                raise ValueError(f"Insight {insight_id} not found")

            insight.is_read = True
            insight.read_at = datetime.utcnow()
            self.db.add(insight)
            await self.db.commit()
            await self.db.refresh(insight)

            logger.info(f"Marked insight {insight_id} as read")
            return insight

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error marking insight read: {str(e)}")
            raise

    async def get_unread_insights(
        self,
        conversation_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[CopilotInsight], int]:
        """Get unread insights.

        Args:
            conversation_id: Optional filter by conversation
            skip: Skip count
            limit: Result limit

        Returns:
            Tuple of insights and count

        Raises:
            Exception: If database operation fails
        """
        try:
            filters = [CopilotInsight.is_read == False]
            if conversation_id:
                filters.append(CopilotInsight.conversation_id == conversation_id)

            query = select(CopilotInsight).where(and_(*filters))
            count_query = select(func.count(CopilotInsight.id)).where(and_(*filters))

            # Get total
            result = await self.db.execute(count_query)
            total = result.scalar() or 0

            # Get paginated
            result = await self.db.execute(
                query.order_by(desc(CopilotInsight.created_at))
                .offset(skip)
                .limit(limit)
            )
            insights = result.scalars().all()

            logger.info(f"Retrieved {len(insights)} unread insights")
            return insights, total

        except Exception as e:
            logger.error(f"Error getting unread insights: {str(e)}")
            raise

    async def get_insights_by_severity(
        self,
        severity: str,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[CopilotInsight], int]:
        """Get insights by severity level.

        Args:
            severity: Severity level (info/warning/critical)
            skip: Skip count
            limit: Result limit

        Returns:
            Tuple of insights and count

        Raises:
            Exception: If database operation fails
        """
        try:
            query = select(CopilotInsight).where(
                CopilotInsight.severity == severity
            )
            count_query = select(func.count(CopilotInsight.id)).where(
                CopilotInsight.severity == severity
            )

            # Get total
            result = await self.db.execute(count_query)
            total = result.scalar() or 0

            # Get paginated
            result = await self.db.execute(
                query.order_by(desc(CopilotInsight.created_at))
                .offset(skip)
                .limit(limit)
            )
            insights = result.scalars().all()

            logger.info(f"Retrieved {len(insights)} {severity} insights")
            return insights, total

        except Exception as e:
            logger.error(f"Error getting insights by severity: {str(e)}")
            raise
