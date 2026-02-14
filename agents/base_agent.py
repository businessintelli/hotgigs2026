import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from agents.events import Event, EventType

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all agents in the system."""

    def __init__(self, agent_name: str, agent_version: str):
        """Initialize the agent.

        Args:
            agent_name: Name of the agent
            agent_version: Version of the agent
        """
        self.agent_name = agent_name
        self.agent_version = agent_version
        self.is_running = False
        self.event_handlers: Dict[EventType, List[callable]] = {}
        self.created_at = datetime.utcnow()

    async def initialize(self) -> None:
        """Initialize the agent and its resources.

        This is called when the agent starts up. Override to add custom initialization logic.
        """
        logger.info(f"Initializing agent: {self.agent_name} v{self.agent_version}")
        self.is_running = True
        await self.on_start()

    async def shutdown(self) -> None:
        """Shutdown the agent and release resources.

        This is called when the agent shuts down. Override to add custom cleanup logic.
        """
        logger.info(f"Shutting down agent: {self.agent_name}")
        self.is_running = False
        await self.on_stop()

    async def process_event(self, event: Event) -> None:
        """Process an event.

        Args:
            event: The event to process

        Raises:
            NotImplementedError: If not overridden by subclass
        """
        try:
            if event.event_type in self.event_handlers:
                for handler in self.event_handlers[event.event_type]:
                    await handler(event)

            logger.debug(f"Agent {self.agent_name} processed event {event.event_type}")
        except Exception as e:
            logger.error(f"Error processing event in {self.agent_name}: {str(e)}")
            await self.on_error(e)

    async def emit_event(
        self,
        event_type: EventType,
        entity_type: str,
        entity_id: int,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Event:
        """Emit an event to the event bus.

        Args:
            event_type: Type of event to emit
            entity_type: Type of entity related to the event
            entity_id: ID of the entity
            payload: Event payload
            correlation_id: Optional correlation ID for tracing
            user_id: Optional user ID who triggered the event

        Returns:
            The emitted event
        """
        import uuid
        from agents.events import Event

        event = Event(
            event_type=event_type,
            event_id=str(uuid.uuid4()),
            source_agent=self.agent_name,
            entity_id=entity_id,
            entity_type=entity_type,
            payload=payload,
            correlation_id=correlation_id or str(uuid.uuid4()),
            user_id=user_id,
        )

        logger.info(f"Agent {self.agent_name} emitted event {event_type} for {entity_type}#{entity_id}")
        return event

    def register_event_handler(self, event_type: EventType, handler: callable) -> None:
        """Register a handler for a specific event type.

        Args:
            event_type: Type of event to handle
            handler: Async callable that handles the event
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []

        self.event_handlers[event_type].append(handler)
        logger.debug(f"Agent {self.agent_name} registered handler for {event_type}")

    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the agent.

        Returns:
            Dictionary with health status information
        """
        return {
            "agent_name": self.agent_name,
            "agent_version": self.agent_version,
            "is_running": self.is_running,
            "created_at": self.created_at.isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.created_at).total_seconds(),
            "status": "healthy" if self.is_running else "unhealthy",
        }

    # Lifecycle hooks

    async def on_start(self) -> None:
        """Called when the agent starts. Override to add custom logic."""
        pass

    async def on_stop(self) -> None:
        """Called when the agent stops. Override to add custom logic."""
        pass

    async def on_error(self, error: Exception) -> None:
        """Called when an error occurs. Override to add custom error handling.

        Args:
            error: The exception that occurred
        """
        logger.error(f"Error in {self.agent_name}: {str(error)}")

    def __repr__(self) -> str:
        return f"<{self.agent_name} v{self.agent_version}>"
