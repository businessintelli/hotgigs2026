"""Tests for Base Agent."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from agents.base_agent import BaseAgent
from agents.events import Event, EventType


class ConcreteAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing."""

    async def on_start(self):
        """Custom start logic."""
        self.startup_called = True

    async def on_stop(self):
        """Custom stop logic."""
        self.shutdown_called = True

    async def on_error(self, error: Exception):
        """Custom error handling."""
        self.last_error = error


class TestBaseAgent:
    """Test suite for BaseAgent."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test agent initialization."""
        agent = ConcreteAgent(agent_name="TestAgent", agent_version="1.0.0")

        assert agent.agent_name == "TestAgent"
        assert agent.agent_version == "1.0.0"
        assert agent.is_running is False
        assert agent.created_at is not None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_agent_startup(self):
        """Test agent startup initialization."""
        agent = ConcreteAgent(agent_name="TestAgent", agent_version="1.0.0")

        await agent.initialize()

        assert agent.is_running is True
        assert agent.startup_called is True

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_agent_shutdown(self):
        """Test agent shutdown."""
        agent = ConcreteAgent(agent_name="TestAgent", agent_version="1.0.0")

        await agent.initialize()
        await agent.shutdown()

        assert agent.is_running is False
        assert agent.shutdown_called is True

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_event_handler_registration(self):
        """Test event handler registration."""
        agent = ConcreteAgent(agent_name="TestAgent", agent_version="1.0.0")

        async def handle_event(event):
            pass

        agent.register_event_handler(EventType.CANDIDATE_CREATED, handle_event)

        assert EventType.CANDIDATE_CREATED in agent.event_handlers
        assert handle_event in agent.event_handlers[EventType.CANDIDATE_CREATED]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_event(self):
        """Test event processing."""
        agent = ConcreteAgent(agent_name="TestAgent", agent_version="1.0.0")

        event_received = []

        async def handle_event(event):
            event_received.append(event)

        agent.register_event_handler(EventType.CANDIDATE_CREATED, handle_event)

        event = Event(
            event_type=EventType.CANDIDATE_CREATED,
            event_id="123",
            source_agent="TestAgent",
            entity_id=1,
            entity_type="Candidate",
            payload={"name": "John Doe"},
        )

        await agent.process_event(event)

        assert len(event_received) == 1
        assert event_received[0].entity_type == "Candidate"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_emit_event(self):
        """Test event emission."""
        agent = ConcreteAgent(agent_name="TestAgent", agent_version="1.0.0")

        event = await agent.emit_event(
            event_type=EventType.CANDIDATE_CREATED,
            entity_type="Candidate",
            entity_id=1,
            payload={"name": "John Doe"},
        )

        assert event.source_agent == "TestAgent"
        assert event.entity_type == "Candidate"
        assert event.entity_id == 1
        assert event.event_id is not None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check."""
        agent = ConcreteAgent(agent_name="TestAgent", agent_version="1.0.0")

        await agent.initialize()
        health = await agent.health_check()

        assert health["agent_name"] == "TestAgent"
        assert health["agent_version"] == "1.0.0"
        assert health["is_running"] is True
        assert health["status"] == "healthy"
        assert "uptime_seconds" in health

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self):
        """Test health check when unhealthy."""
        agent = ConcreteAgent(agent_name="TestAgent", agent_version="1.0.0")

        health = await agent.health_check()

        assert health["is_running"] is False
        assert health["status"] == "unhealthy"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_multiple_event_handlers(self):
        """Test multiple event handlers for same event type."""
        agent = ConcreteAgent(agent_name="TestAgent", agent_version="1.0.0")

        handler_calls = []

        async def handler1(event):
            handler_calls.append("handler1")

        async def handler2(event):
            handler_calls.append("handler2")

        agent.register_event_handler(EventType.CANDIDATE_CREATED, handler1)
        agent.register_event_handler(EventType.CANDIDATE_CREATED, handler2)

        event = Event(
            event_type=EventType.CANDIDATE_CREATED,
            event_id="123",
            source_agent="TestAgent",
            entity_id=1,
            entity_type="Candidate",
            payload={},
        )

        await agent.process_event(event)

        assert len(handler_calls) == 2
        assert "handler1" in handler_calls
        assert "handler2" in handler_calls

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_event_handler_error_handling(self):
        """Test error handling in event processing."""
        agent = ConcreteAgent(agent_name="TestAgent", agent_version="1.0.0")

        async def failing_handler(event):
            raise ValueError("Handler error")

        agent.register_event_handler(EventType.CANDIDATE_CREATED, failing_handler)

        event = Event(
            event_type=EventType.CANDIDATE_CREATED,
            event_id="123",
            source_agent="TestAgent",
            entity_id=1,
            entity_type="Candidate",
            payload={},
        )

        await agent.process_event(event)

        assert isinstance(agent.last_error, ValueError)

    @pytest.mark.unit
    def test_agent_repr(self):
        """Test agent string representation."""
        agent = ConcreteAgent(agent_name="TestAgent", agent_version="1.0.0")

        repr_str = repr(agent)
        assert "TestAgent" in repr_str
        assert "1.0.0" in repr_str

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_emit_event_with_user_id(self):
        """Test event emission with user ID."""
        agent = ConcreteAgent(agent_name="TestAgent", agent_version="1.0.0")

        event = await agent.emit_event(
            event_type=EventType.CANDIDATE_CREATED,
            entity_type="Candidate",
            entity_id=1,
            payload={},
            user_id=42,
        )

        assert event.user_id == 42

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_emit_event_with_correlation_id(self):
        """Test event emission with correlation ID."""
        agent = ConcreteAgent(agent_name="TestAgent", agent_version="1.0.0")

        correlation_id = "corr-12345"
        event = await agent.emit_event(
            event_type=EventType.CANDIDATE_CREATED,
            entity_type="Candidate",
            entity_id=1,
            payload={},
            correlation_id=correlation_id,
        )

        assert event.correlation_id == correlation_id

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_multiple_event_types(self):
        """Test handling multiple event types."""
        agent = ConcreteAgent(agent_name="TestAgent", agent_version="1.0.0")

        received_events = []

        async def handle_candidate_created(event):
            received_events.append(("candidate_created", event.entity_id))

        async def handle_requirement_created(event):
            received_events.append(("requirement_created", event.entity_id))

        agent.register_event_handler(
            EventType.CANDIDATE_CREATED, handle_candidate_created
        )
        agent.register_event_handler(
            EventType.REQUIREMENT_CREATED, handle_requirement_created
        )

        event1 = Event(
            event_type=EventType.CANDIDATE_CREATED,
            event_id="123",
            source_agent="TestAgent",
            entity_id=1,
            entity_type="Candidate",
            payload={},
        )

        event2 = Event(
            event_type=EventType.REQUIREMENT_CREATED,
            event_id="124",
            source_agent="TestAgent",
            entity_id=10,
            entity_type="Requirement",
            payload={},
        )

        await agent.process_event(event1)
        await agent.process_event(event2)

        assert len(received_events) == 2
        assert received_events[0] == ("candidate_created", 1)
        assert received_events[1] == ("requirement_created", 10)
