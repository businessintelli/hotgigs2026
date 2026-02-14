import logging
import json
import asyncio
from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional, Any
from agents.events import Event, EventType
import redis.asyncio as aioredis
import aio_pika

logger = logging.getLogger(__name__)


class EventBroker(ABC):
    """Abstract base class for event brokers."""

    @abstractmethod
    async def publish(self, event: Event, queue: Optional[str] = None) -> None:
        """Publish an event.

        Args:
            event: The event to publish
            queue: Optional queue name
        """
        pass

    @abstractmethod
    async def subscribe(self, event_type: EventType, callback: Callable) -> None:
        """Subscribe to an event type.

        Args:
            event_type: Type of event to subscribe to
            callback: Async callback function
        """
        pass

    @abstractmethod
    async def unsubscribe(self, event_type: EventType, callback: Callable) -> None:
        """Unsubscribe from an event type.

        Args:
            event_type: Type of event to unsubscribe from
            callback: Callback function to remove
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the broker connection."""
        pass


class RedisPubSubBroker(EventBroker):
    """Redis pub/sub event broker for lightweight events."""

    def __init__(self, redis_url: str):
        """Initialize Redis pub/sub broker.

        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None
        self.subscriptions: Dict[str, List[Callable]] = {}

    async def initialize(self) -> None:
        """Initialize Redis connection."""
        try:
            self.redis = await aioredis.from_url(self.redis_url)
            logger.info("Redis pub/sub broker initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Redis broker: {str(e)}")
            raise

    async def publish(self, event: Event, queue: Optional[str] = None) -> None:
        """Publish an event to Redis pub/sub.

        Args:
            event: The event to publish
            queue: Not used for pub/sub
        """
        if not self.redis:
            logger.error("Redis not initialized")
            return

        channel = f"events:{event.event_type.value}"
        try:
            await self.redis.publish(channel, event.to_json())
            logger.debug(f"Published event {event.event_id} to channel {channel}")
        except Exception as e:
            logger.error(f"Failed to publish event: {str(e)}")

    async def subscribe(self, event_type: EventType, callback: Callable) -> None:
        """Subscribe to an event type.

        Args:
            event_type: Type of event to subscribe to
            callback: Async callback function
        """
        channel = f"events:{event_type.value}"

        if channel not in self.subscriptions:
            self.subscriptions[channel] = []

        self.subscriptions[channel].append(callback)
        logger.debug(f"Subscribed to channel {channel}")

    async def unsubscribe(self, event_type: EventType, callback: Callable) -> None:
        """Unsubscribe from an event type.

        Args:
            event_type: Type of event to unsubscribe from
            callback: Callback function to remove
        """
        channel = f"events:{event_type.value}"

        if channel in self.subscriptions:
            self.subscriptions[channel].remove(callback)
            logger.debug(f"Unsubscribed from channel {channel}")

    async def close(self) -> None:
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            logger.info("Redis pub/sub broker closed")


class RabbitMQBroker(EventBroker):
    """RabbitMQ event broker for durable task queues."""

    def __init__(self, rabbitmq_url: str, queue_prefix: str = "hr_platform"):
        """Initialize RabbitMQ broker.

        Args:
            rabbitmq_url: RabbitMQ connection URL
            queue_prefix: Prefix for queue names
        """
        self.rabbitmq_url = rabbitmq_url
        self.queue_prefix = queue_prefix
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchanges: Dict[str, aio_pika.Exchange] = {}

    async def initialize(self) -> None:
        """Initialize RabbitMQ connection."""
        try:
            self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
            self.channel = await self.connection.channel()
            logger.info("RabbitMQ broker initialized")
        except Exception as e:
            logger.error(f"Failed to initialize RabbitMQ broker: {str(e)}")
            raise

    async def _get_exchange(self, exchange_name: str) -> aio_pika.Exchange:
        """Get or create an exchange.

        Args:
            exchange_name: Name of the exchange

        Returns:
            The exchange object
        """
        if exchange_name not in self.exchanges:
            exchange = await self.channel.declare_exchange(
                exchange_name,
                aio_pika.ExchangeType.TOPIC,
                durable=True,
            )
            self.exchanges[exchange_name] = exchange

        return self.exchanges[exchange_name]

    async def publish(self, event: Event, queue: Optional[str] = None) -> None:
        """Publish an event to RabbitMQ.

        Args:
            event: The event to publish
            queue: Optional queue name
        """
        if not self.channel:
            logger.error("RabbitMQ not initialized")
            return

        try:
            exchange = await self._get_exchange(f"{self.queue_prefix}.events")
            routing_key = event.event_type.value

            message = aio_pika.Message(
                body=event.to_json().encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )

            await exchange.publish(message, routing_key=routing_key)
            logger.debug(f"Published event {event.event_id} to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to publish event to RabbitMQ: {str(e)}")

    async def subscribe(self, event_type: EventType, callback: Callable) -> None:
        """Subscribe to an event type.

        Args:
            event_type: Type of event to subscribe to
            callback: Async callback function
        """
        if not self.channel:
            logger.error("RabbitMQ not initialized")
            return

        try:
            exchange = await self._get_exchange(f"{self.queue_prefix}.events")
            queue_name = f"{self.queue_prefix}.{event_type.value}"

            queue = await self.channel.declare_queue(queue_name, durable=True)
            await queue.bind(exchange, routing_key=event_type.value)

            async def queue_callback(message: aio_pika.IncomingMessage) -> None:
                async with message.process():
                    event = Event.from_json(message.body.decode())
                    await callback(event)

            await queue.consume(queue_callback)
            logger.debug(f"Subscribed to event type {event_type.value}")
        except Exception as e:
            logger.error(f"Failed to subscribe to event: {str(e)}")

    async def unsubscribe(self, event_type: EventType, callback: Callable) -> None:
        """Unsubscribe from an event type.

        Args:
            event_type: Type of event to unsubscribe from
            callback: Not used for RabbitMQ
        """
        logger.debug(f"Unsubscribed from event type {event_type.value}")

    async def close(self) -> None:
        """Close RabbitMQ connection."""
        if self.connection:
            await self.connection.close()
            logger.info("RabbitMQ broker closed")


class EventBus:
    """Central event bus that coordinates between brokers."""

    def __init__(
        self,
        redis_broker: Optional[RedisPubSubBroker] = None,
        rabbitmq_broker: Optional[RabbitMQBroker] = None,
    ):
        """Initialize event bus.

        Args:
            redis_broker: Optional Redis pub/sub broker
            rabbitmq_broker: Optional RabbitMQ broker
        """
        self.redis_broker = redis_broker
        self.rabbitmq_broker = rabbitmq_broker
        self.local_subscribers: Dict[EventType, List[Callable]] = {}
        self.dead_letter_queue: List[Event] = []

    async def initialize(self) -> None:
        """Initialize all brokers."""
        if self.redis_broker:
            await self.redis_broker.initialize()

        if self.rabbitmq_broker:
            await self.rabbitmq_broker.initialize()

        logger.info("Event bus initialized")

    async def publish(self, event: Event, use_rabbitmq: bool = False) -> None:
        """Publish an event to all configured brokers.

        Args:
            event: The event to publish
            use_rabbitmq: Whether to use RabbitMQ (for durable queues)
        """
        try:
            if use_rabbitmq and self.rabbitmq_broker:
                await self.rabbitmq_broker.publish(event)
            elif self.redis_broker:
                await self.redis_broker.publish(event)

            # Call local subscribers
            if event.event_type in self.local_subscribers:
                for callback in self.local_subscribers[event.event_type]:
                    await callback(event)

        except Exception as e:
            logger.error(f"Failed to publish event: {str(e)}")
            self.dead_letter_queue.append(event)

    async def subscribe(
        self,
        event_type: EventType,
        callback: Callable,
        use_rabbitmq: bool = False,
    ) -> None:
        """Subscribe to an event type.

        Args:
            event_type: Type of event to subscribe to
            callback: Async callback function
            use_rabbitmq: Whether to use RabbitMQ
        """
        # Subscribe locally
        if event_type not in self.local_subscribers:
            self.local_subscribers[event_type] = []

        self.local_subscribers[event_type].append(callback)

        # Subscribe to brokers
        if use_rabbitmq and self.rabbitmq_broker:
            await self.rabbitmq_broker.subscribe(event_type, callback)
        elif self.redis_broker:
            await self.redis_broker.subscribe(event_type, callback)

    async def unsubscribe(self, event_type: EventType, callback: Callable) -> None:
        """Unsubscribe from an event type.

        Args:
            event_type: Type of event to unsubscribe from
            callback: Callback function to remove
        """
        if event_type in self.local_subscribers:
            self.local_subscribers[event_type].remove(callback)

        if self.redis_broker:
            await self.redis_broker.unsubscribe(event_type, callback)

        if self.rabbitmq_broker:
            await self.rabbitmq_broker.unsubscribe(event_type, callback)

    async def retry_dead_letter_queue(self) -> None:
        """Retry events in the dead letter queue."""
        failed_events = []

        for event in self.dead_letter_queue:
            try:
                if event.should_retry:
                    event.retry_count += 1
                    await self.publish(event)
                else:
                    logger.error(f"Event {event.event_id} exceeded max retries")
                    failed_events.append(event)
            except Exception as e:
                logger.error(f"Failed to retry event {event.event_id}: {str(e)}")
                failed_events.append(event)

        self.dead_letter_queue = failed_events

    async def close(self) -> None:
        """Close all brokers."""
        if self.redis_broker:
            await self.redis_broker.close()

        if self.rabbitmq_broker:
            await self.rabbitmq_broker.close()

        logger.info("Event bus closed")
