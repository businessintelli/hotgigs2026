"""Messaging service for managing integrations and notifications."""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.messaging import MessagingIntegration, MessagingChannel, NotificationRoute, MessagingLog
from schemas.messaging import (
    MessagingIntegrationCreate,
    MessagingIntegrationUpdate,
    MessagingChannelCreate,
    MessagingChannelUpdate,
    NotificationRouteCreate,
    NotificationRouteUpdate,
)

logger = logging.getLogger(__name__)


class MessagingService:
    """Service for messaging integrations."""

    def __init__(self, db: AsyncSession):
        """Initialize messaging service.

        Args:
            db: Async database session
        """
        self.db = db

    async def create_integration(
        self,
        platform: str,
        workspace_name: str,
        workspace_id: str,
        bot_token_encrypted: Optional[str] = None,
        webhook_url: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        setup_by: Optional[int] = None,
    ) -> MessagingIntegration:
        """Create messaging integration.

        Args:
            platform: slack or teams
            workspace_name: Workspace/organization name
            workspace_id: Workspace ID from platform
            bot_token_encrypted: Encrypted bot token
            webhook_url: Webhook URL for Teams
            config: Additional configuration
            setup_by: User ID who set up integration

        Returns:
            Created integration

        Raises:
            ValueError: If integration already exists for workspace
        """
        # Check if integration already exists
        existing = await self.get_integration_by_workspace(workspace_id)
        if existing:
            raise ValueError(f"Integration already exists for workspace {workspace_id}")

        integration = MessagingIntegration(
            platform=platform,
            workspace_name=workspace_name,
            workspace_id=workspace_id,
            bot_token_encrypted=bot_token_encrypted,
            webhook_url=webhook_url,
            status="active",
            config=config or {},
            setup_by=setup_by,
            last_connected_at=datetime.utcnow(),
        )

        self.db.add(integration)
        await self.db.commit()
        await self.db.refresh(integration)

        logger.info(f"Messaging integration created: {platform} - {workspace_name}")
        return integration

    async def get_integration_by_id(self, integration_id: int) -> Optional[MessagingIntegration]:
        """Get integration by ID.

        Args:
            integration_id: Integration ID

        Returns:
            Integration or None
        """
        stmt = select(MessagingIntegration).where(MessagingIntegration.id == integration_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_integration_by_workspace(self, workspace_id: str) -> Optional[MessagingIntegration]:
        """Get integration by workspace ID.

        Args:
            workspace_id: Workspace ID

        Returns:
            Integration or None
        """
        stmt = select(MessagingIntegration).where(MessagingIntegration.workspace_id == workspace_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_integrations(self, platform: Optional[str] = None) -> List[MessagingIntegration]:
        """List all integrations.

        Args:
            platform: Optional filter by platform

        Returns:
            List of integrations
        """
        stmt = select(MessagingIntegration).order_by(MessagingIntegration.created_at.desc())
        if platform:
            stmt = stmt.where(MessagingIntegration.platform == platform)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_integration(
        self, integration_id: int, update_data: MessagingIntegrationUpdate
    ) -> MessagingIntegration:
        """Update integration.

        Args:
            integration_id: Integration ID
            update_data: Update data

        Returns:
            Updated integration

        Raises:
            ValueError: If integration not found
        """
        integration = await self.get_integration_by_id(integration_id)
        if not integration:
            raise ValueError(f"Integration {integration_id} not found")

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(integration, key, value)

        await self.db.commit()
        await self.db.refresh(integration)

        logger.info(f"Integration {integration_id} updated")
        return integration

    async def delete_integration(self, integration_id: int) -> None:
        """Delete integration.

        Args:
            integration_id: Integration ID

        Raises:
            ValueError: If integration not found
        """
        integration = await self.get_integration_by_id(integration_id)
        if not integration:
            raise ValueError(f"Integration {integration_id} not found")

        await self.db.delete(integration)
        await self.db.commit()

        logger.info(f"Integration {integration_id} deleted")

    # Channel management

    async def create_channel(self, channel_data: MessagingChannelCreate) -> MessagingChannel:
        """Create messaging channel.

        Args:
            channel_data: Channel creation data

        Returns:
            Created channel

        Raises:
            ValueError: If integration not found or channel exists
        """
        integration = await self.get_integration_by_id(channel_data.integration_id)
        if not integration:
            raise ValueError(f"Integration {channel_data.integration_id} not found")

        channel = MessagingChannel(
            integration_id=channel_data.integration_id,
            channel_id=channel_data.channel_id,
            channel_name=channel_data.channel_name,
            channel_type=channel_data.channel_type,
            purpose=channel_data.purpose,
            is_default=channel_data.is_default,
            linked_requirement_id=channel_data.linked_requirement_id,
            linked_customer_id=channel_data.linked_customer_id,
        )

        self.db.add(channel)
        await self.db.commit()
        await self.db.refresh(channel)

        logger.info(f"Channel created: {channel_data.channel_name}")
        return channel

    async def get_channel_by_id(self, channel_id: int) -> Optional[MessagingChannel]:
        """Get channel by ID.

        Args:
            channel_id: Channel ID

        Returns:
            Channel or None
        """
        stmt = select(MessagingChannel).where(MessagingChannel.id == channel_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_channels(self, integration_id: Optional[int] = None) -> List[MessagingChannel]:
        """List channels.

        Args:
            integration_id: Optional filter by integration

        Returns:
            List of channels
        """
        stmt = select(MessagingChannel).where(MessagingChannel.is_active == True).order_by(MessagingChannel.channel_name)
        if integration_id:
            stmt = stmt.where(MessagingChannel.integration_id == integration_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_channel(self, channel_id: int, update_data: MessagingChannelUpdate) -> MessagingChannel:
        """Update channel.

        Args:
            channel_id: Channel ID
            update_data: Update data

        Returns:
            Updated channel

        Raises:
            ValueError: If channel not found
        """
        channel = await self.get_channel_by_id(channel_id)
        if not channel:
            raise ValueError(f"Channel {channel_id} not found")

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(channel, key, value)

        await self.db.commit()
        await self.db.refresh(channel)

        logger.info(f"Channel {channel_id} updated")
        return channel

    async def delete_channel(self, channel_id: int) -> None:
        """Delete channel.

        Args:
            channel_id: Channel ID

        Raises:
            ValueError: If channel not found
        """
        channel = await self.get_channel_by_id(channel_id)
        if not channel:
            raise ValueError(f"Channel {channel_id} not found")

        await self.db.delete(channel)
        await self.db.commit()

        logger.info(f"Channel {channel_id} deleted")

    # Notification route management

    async def create_notification_route(
        self,
        event_type: str,
        channel_id: int,
        is_enabled: bool = True,
        template: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        created_by: Optional[int] = None,
    ) -> NotificationRoute:
        """Create notification route.

        Args:
            event_type: Event type to route
            channel_id: Target channel
            is_enabled: Enable/disable route
            template: Custom message template
            filters: Event filters
            created_by: User who created route

        Returns:
            Created route

        Raises:
            ValueError: If channel not found
        """
        channel = await self.get_channel_by_id(channel_id)
        if not channel:
            raise ValueError(f"Channel {channel_id} not found")

        route = NotificationRoute(
            event_type=event_type,
            channel_id=channel_id,
            is_enabled=is_enabled,
            template=template,
            filters=filters or {},
            created_by=created_by,
        )

        self.db.add(route)
        await self.db.commit()
        await self.db.refresh(route)

        logger.info(f"Notification route created: {event_type} -> {channel.channel_name}")
        return route

    async def get_route_by_id(self, route_id: int) -> Optional[NotificationRoute]:
        """Get route by ID.

        Args:
            route_id: Route ID

        Returns:
            Route or None
        """
        stmt = select(NotificationRoute).where(NotificationRoute.id == route_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_routes_by_event(self, event_type: str) -> List[NotificationRoute]:
        """Get routes for event type.

        Args:
            event_type: Event type

        Returns:
            List of routes
        """
        stmt = (
            select(NotificationRoute)
            .where(and_(NotificationRoute.event_type == event_type, NotificationRoute.is_enabled == True))
            .options(selectinload(NotificationRoute.channel))
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list_routes(self) -> List[NotificationRoute]:
        """List all routes.

        Returns:
            List of routes
        """
        stmt = select(NotificationRoute).order_by(NotificationRoute.event_type)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_route(self, route_id: int, update_data: NotificationRouteUpdate) -> NotificationRoute:
        """Update route.

        Args:
            route_id: Route ID
            update_data: Update data

        Returns:
            Updated route

        Raises:
            ValueError: If route not found
        """
        route = await self.get_route_by_id(route_id)
        if not route:
            raise ValueError(f"Route {route_id} not found")

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(route, key, value)

        await self.db.commit()
        await self.db.refresh(route)

        logger.info(f"Route {route_id} updated")
        return route

    async def delete_route(self, route_id: int) -> None:
        """Delete route.

        Args:
            route_id: Route ID

        Raises:
            ValueError: If route not found
        """
        route = await self.get_route_by_id(route_id)
        if not route:
            raise ValueError(f"Route {route_id} not found")

        await self.db.delete(route)
        await self.db.commit()

        logger.info(f"Route {route_id} deleted")

    # Messaging log

    async def create_log_entry(
        self,
        integration_id: int,
        message_type: str,
        channel_id: Optional[str] = None,
        recipient: Optional[str] = None,
        event_type: Optional[str] = None,
        content_preview: Optional[str] = None,
        external_message_id: Optional[str] = None,
        status: str = "sent",
    ) -> MessagingLog:
        """Create messaging log entry.

        Args:
            integration_id: Integration ID
            message_type: Type of message
            channel_id: Channel ID
            recipient: Recipient email/id
            event_type: Event type
            content_preview: Message preview
            external_message_id: External platform message ID
            status: Message status

        Returns:
            Created log entry
        """
        log = MessagingLog(
            integration_id=integration_id,
            channel_id=channel_id,
            recipient=recipient,
            message_type=message_type,
            event_type=event_type,
            content_preview=content_preview,
            external_message_id=external_message_id,
            status=status,
        )

        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)

        logger.debug(f"Log entry created: {message_type} in {channel_id}")
        return log

    async def get_logs(
        self,
        integration_id: Optional[int] = None,
        message_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[List[MessagingLog], int]:
        """Get messaging logs.

        Args:
            integration_id: Filter by integration
            message_type: Filter by message type
            status: Filter by status
            limit: Result limit
            offset: Result offset

        Returns:
            Tuple of logs and total count
        """
        stmt = select(MessagingLog)

        if integration_id:
            stmt = stmt.where(MessagingLog.integration_id == integration_id)
        if message_type:
            stmt = stmt.where(MessagingLog.message_type == message_type)
        if status:
            stmt = stmt.where(MessagingLog.status == status)

        count_stmt = stmt.select_entity_from(MessagingLog)
        count_result = await self.db.execute(select(func.count()).select_from(count_stmt.subquery()))
        total = count_result.scalar()

        stmt = stmt.order_by(desc(MessagingLog.sent_at)).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        logs = result.scalars().all()

        return logs, total

    async def get_analytics(self, integration_id: Optional[int] = None, days: int = 30) -> Dict[str, Any]:
        """Get messaging analytics.

        Args:
            integration_id: Filter by integration
            days: Days to analyze

        Returns:
            Analytics data
        """
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        stmt = select(MessagingLog).where(MessagingLog.sent_at >= cutoff_date)
        if integration_id:
            stmt = stmt.where(MessagingLog.integration_id == integration_id)

        result = await self.db.execute(stmt)
        logs = result.scalars().all()

        total_messages = len(logs)
        delivered = len([l for l in logs if l.status == "delivered"])
        failed = len([l for l in logs if l.status == "failed"])

        messages_by_type = {}
        messages_by_channel = {}

        for log in logs:
            messages_by_type[log.message_type] = messages_by_type.get(log.message_type, 0) + 1
            if log.channel_id:
                messages_by_channel[log.channel_id] = messages_by_channel.get(log.channel_id, 0) + 1

        analytics = {
            "total_messages": total_messages,
            "delivered": delivered,
            "failed": failed,
            "delivery_rate": (delivered / total_messages * 100) if total_messages > 0 else 0,
            "messages_by_type": messages_by_type,
            "messages_by_channel": messages_by_channel,
            "period_days": days,
        }

        return analytics
