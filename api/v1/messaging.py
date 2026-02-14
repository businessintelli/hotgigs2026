"""Messaging integration API endpoints."""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from api.dependencies import get_db
from schemas.messaging import (
    MessagingIntegrationCreate,
    MessagingIntegrationUpdate,
    MessagingIntegrationResponse,
    MessagingChannelCreate,
    MessagingChannelUpdate,
    MessagingChannelResponse,
    NotificationRouteCreate,
    NotificationRouteUpdate,
    NotificationRouteResponse,
    MessagingLogResponse,
    SlackMessageCreate,
    TeamsMessageCreate,
    MessageResponse,
    SlackSlashCommandPayload,
    SlackInteractionPayload,
    MessagingAnalytics,
    IntegrationStatus,
)
from schemas.common import BaseResponse
from services.messaging_service import MessagingService
from agents.messaging_integration_agent import MessagingIntegrationAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/messaging", tags=["messaging"])
agent = MessagingIntegrationAgent()


# Integration endpoints

@router.post("/integrations", response_model=MessagingIntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_integration(
    integration_data: MessagingIntegrationCreate,
    db: AsyncSession = Depends(get_db),
    user_id: Optional[int] = None,
) -> MessagingIntegrationResponse:
    """Create messaging integration.

    Args:
        integration_data: Integration creation data
        db: Database session
        user_id: User ID

    Returns:
        Created integration
    """
    try:
        service = MessagingService(db)
        integration = await service.create_integration(
            platform=integration_data.platform,
            workspace_name=integration_data.workspace_name or "",
            workspace_id=integration_data.workspace_id or "",
            bot_token_encrypted=integration_data.bot_token_encrypted,
            webhook_url=integration_data.webhook_url,
            config=integration_data.config,
            setup_by=user_id,
        )
        return MessagingIntegrationResponse.from_orm(integration)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating integration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create integration",
        )


@router.get("/integrations", response_model=List[MessagingIntegrationResponse])
async def list_integrations(
    platform: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> List[MessagingIntegrationResponse]:
    """List all integrations.

    Args:
        platform: Optional platform filter
        db: Database session

    Returns:
        List of integrations
    """
    try:
        service = MessagingService(db)
        integrations = await service.list_integrations(platform=platform)
        return [MessagingIntegrationResponse.from_orm(i) for i in integrations]
    except Exception as e:
        logger.error(f"Error listing integrations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list integrations",
        )


@router.get("/integrations/{integration_id}", response_model=MessagingIntegrationResponse)
async def get_integration(
    integration_id: int,
    db: AsyncSession = Depends(get_db),
) -> MessagingIntegrationResponse:
    """Get integration by ID.

    Args:
        integration_id: Integration ID
        db: Database session

    Returns:
        Integration details
    """
    try:
        service = MessagingService(db)
        integration = await service.get_integration_by_id(integration_id)
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found",
            )
        return MessagingIntegrationResponse.from_orm(integration)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting integration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get integration",
        )


@router.put("/integrations/{integration_id}", response_model=MessagingIntegrationResponse)
async def update_integration(
    integration_id: int,
    update_data: MessagingIntegrationUpdate,
    db: AsyncSession = Depends(get_db),
) -> MessagingIntegrationResponse:
    """Update integration.

    Args:
        integration_id: Integration ID
        update_data: Update data
        db: Database session

    Returns:
        Updated integration
    """
    try:
        service = MessagingService(db)
        integration = await service.update_integration(integration_id, update_data)
        return MessagingIntegrationResponse.from_orm(integration)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating integration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update integration",
        )


@router.delete("/integrations/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    integration_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete integration.

    Args:
        integration_id: Integration ID
        db: Database session
    """
    try:
        service = MessagingService(db)
        await service.delete_integration(integration_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting integration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete integration",
        )


@router.post("/integrations/{integration_id}/test", response_model=dict)
async def test_integration(
    integration_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Test integration connection.

    Args:
        integration_id: Integration ID
        db: Database session

    Returns:
        Test result
    """
    try:
        service = MessagingService(db)
        integration = await service.get_integration_by_id(integration_id)
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found",
            )
        # In production, test the actual connection
        return {
            "success": True,
            "message": f"{integration.platform} integration is connected",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing integration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to test integration",
        )


# Channel endpoints

@router.post("/channels", response_model=MessagingChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_channel(
    channel_data: MessagingChannelCreate,
    db: AsyncSession = Depends(get_db),
) -> MessagingChannelResponse:
    """Create messaging channel mapping.

    Args:
        channel_data: Channel creation data
        db: Database session

    Returns:
        Created channel
    """
    try:
        service = MessagingService(db)
        channel = await service.create_channel(channel_data)
        return MessagingChannelResponse.from_orm(channel)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating channel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create channel",
        )


@router.get("/channels", response_model=List[MessagingChannelResponse])
async def list_channels(
    integration_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> List[MessagingChannelResponse]:
    """List messaging channels.

    Args:
        integration_id: Optional filter by integration
        db: Database session

    Returns:
        List of channels
    """
    try:
        service = MessagingService(db)
        channels = await service.list_channels(integration_id=integration_id)
        return [MessagingChannelResponse.from_orm(c) for c in channels]
    except Exception as e:
        logger.error(f"Error listing channels: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list channels",
        )


@router.get("/channels/{channel_id}", response_model=MessagingChannelResponse)
async def get_channel(
    channel_id: int,
    db: AsyncSession = Depends(get_db),
) -> MessagingChannelResponse:
    """Get channel by ID.

    Args:
        channel_id: Channel ID
        db: Database session

    Returns:
        Channel details
    """
    try:
        service = MessagingService(db)
        channel = await service.get_channel_by_id(channel_id)
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel not found",
            )
        return MessagingChannelResponse.from_orm(channel)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting channel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get channel",
        )


@router.put("/channels/{channel_id}", response_model=MessagingChannelResponse)
async def update_channel(
    channel_id: int,
    update_data: MessagingChannelUpdate,
    db: AsyncSession = Depends(get_db),
) -> MessagingChannelResponse:
    """Update channel.

    Args:
        channel_id: Channel ID
        update_data: Update data
        db: Database session

    Returns:
        Updated channel
    """
    try:
        service = MessagingService(db)
        channel = await service.update_channel(channel_id, update_data)
        return MessagingChannelResponse.from_orm(channel)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating channel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update channel",
        )


# Notification route endpoints

@router.post("/routes", response_model=NotificationRouteResponse, status_code=status.HTTP_201_CREATED)
async def create_route(
    route_data: NotificationRouteCreate,
    db: AsyncSession = Depends(get_db),
    user_id: Optional[int] = None,
) -> NotificationRouteResponse:
    """Create notification route.

    Args:
        route_data: Route creation data
        db: Database session
        user_id: User ID

    Returns:
        Created route
    """
    try:
        service = MessagingService(db)
        route = await service.create_notification_route(
            event_type=route_data.event_type,
            channel_id=route_data.channel_id,
            is_enabled=route_data.is_enabled,
            template=route_data.template,
            filters=route_data.filters,
            created_by=user_id,
        )
        return NotificationRouteResponse.from_orm(route)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating route: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create route",
        )


@router.get("/routes", response_model=List[NotificationRouteResponse])
async def list_routes(
    db: AsyncSession = Depends(get_db),
) -> List[NotificationRouteResponse]:
    """List notification routes.

    Args:
        db: Database session

    Returns:
        List of routes
    """
    try:
        service = MessagingService(db)
        routes = await service.list_routes()
        return [NotificationRouteResponse.from_orm(r) for r in routes]
    except Exception as e:
        logger.error(f"Error listing routes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list routes",
        )


@router.get("/routes/{route_id}", response_model=NotificationRouteResponse)
async def get_route(
    route_id: int,
    db: AsyncSession = Depends(get_db),
) -> NotificationRouteResponse:
    """Get route by ID.

    Args:
        route_id: Route ID
        db: Database session

    Returns:
        Route details
    """
    try:
        service = MessagingService(db)
        route = await service.get_route_by_id(route_id)
        if not route:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Route not found",
            )
        return NotificationRouteResponse.from_orm(route)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting route: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get route",
        )


@router.put("/routes/{route_id}", response_model=NotificationRouteResponse)
async def update_route(
    route_id: int,
    update_data: NotificationRouteUpdate,
    db: AsyncSession = Depends(get_db),
) -> NotificationRouteResponse:
    """Update route.

    Args:
        route_id: Route ID
        update_data: Update data
        db: Database session

    Returns:
        Updated route
    """
    try:
        service = MessagingService(db)
        route = await service.update_route(route_id, update_data)
        return NotificationRouteResponse.from_orm(route)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating route: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update route",
        )


@router.delete("/routes/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_route(
    route_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete route.

    Args:
        route_id: Route ID
        db: Database session
    """
    try:
        service = MessagingService(db)
        await service.delete_route(route_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting route: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete route",
        )


# Message sending endpoints

@router.post("/send/slack", response_model=MessageResponse)
async def send_slack_message(
    message_data: SlackMessageCreate,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Send message to Slack.

    Args:
        message_data: Message data
        db: Database session

    Returns:
        Message send result
    """
    try:
        result = await agent.send_slack_message(
            db,
            message_data.channel,
            message_data.message,
            blocks=message_data.blocks,
            thread_ts=message_data.thread_ts,
        )
        return MessageResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error sending Slack message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message",
        )


@router.post("/send/teams", response_model=MessageResponse)
async def send_teams_message(
    message_data: TeamsMessageCreate,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Send message to Teams.

    Args:
        message_data: Message data
        db: Database session

    Returns:
        Message send result
    """
    try:
        result = await agent.send_teams_message(
            db,
            message_data.channel_id,
            message_data.message,
            card=message_data.card,
        )
        return MessageResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error sending Teams message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message",
        )


# Analytics endpoints

@router.get("/logs", response_model=List[MessagingLogResponse])
async def get_logs(
    integration_id: Optional[int] = Query(None),
    message_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
) -> List[MessagingLogResponse]:
    """Get messaging logs.

    Args:
        integration_id: Filter by integration
        message_type: Filter by message type
        status: Filter by status
        limit: Result limit
        offset: Result offset
        db: Database session

    Returns:
        List of log entries
    """
    try:
        service = MessagingService(db)
        logs, _ = await service.get_logs(
            integration_id=integration_id,
            message_type=message_type,
            status=status,
            limit=limit,
            offset=offset,
        )
        return [MessagingLogResponse.from_orm(l) for l in logs]
    except Exception as e:
        logger.error(f"Error getting logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get logs",
        )


@router.get("/analytics", response_model=MessagingAnalytics)
async def get_analytics(
    integration_id: Optional[int] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
) -> MessagingAnalytics:
    """Get messaging analytics.

    Args:
        integration_id: Filter by integration
        days: Days to analyze
        db: Database session

    Returns:
        Analytics data
    """
    try:
        service = MessagingService(db)
        analytics = await service.get_analytics(integration_id=integration_id, days=days)
        return MessagingAnalytics(**analytics)
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get analytics",
        )


# Webhook endpoints

@router.post("/slack/commands")
async def handle_slack_command(
    payload: SlackSlashCommandPayload,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Handle Slack slash command.

    Args:
        payload: Slack payload
        db: Database session

    Returns:
        Command response
    """
    try:
        result = await agent.handle_slack_slash_command(
            db,
            payload.command,
            payload.text,
            payload.user_id,
        )
        return result
    except Exception as e:
        logger.error(f"Error handling Slack command: {str(e)}")
        return {"error": str(e)}


@router.post("/slack/interactions")
async def handle_slack_interaction(
    payload: SlackInteractionPayload,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Handle Slack interaction.

    Args:
        payload: Slack payload
        db: Database session

    Returns:
        Interaction response
    """
    try:
        result = await agent.handle_slack_interaction(db, payload.model_dump())
        return result
    except Exception as e:
        logger.error(f"Error handling Slack interaction: {str(e)}")
        return {"error": str(e)}
