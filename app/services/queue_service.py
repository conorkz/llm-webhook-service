import aio_pika
import json
from ..config import get_settings
import logging
import asyncio
from typing import Callable

logger = logging.getLogger(__name__)
settings = get_settings()

class QueueService:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue_name = "llm_requests"
        self.max_retries = 5
        self.retry_delay = 5

    async def connect(self):
        if not self.connection:
            for attempt in range(self.max_retries):
                try:
                    self.connection = await aio_pika.connect_robust(
                        settings.RABBITMQ_URL,
                        timeout=30
                    )
                    self.channel = await self.connection.channel()
                    await self.channel.declare_queue(self.queue_name, durable=True)
                    logger.info("Successfully connected to RabbitMQ")
                    break
                except Exception as e:
                    logger.error(f"Failed to connect to RabbitMQ (attempt {attempt + 1}/{self.max_retries}): {e}")
                    if attempt + 1 < self.max_retries:
                        await asyncio.sleep(self.retry_delay)
                    else:
                        raise

    async def publish_message(self, message_data: dict):
        await self.connect()
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message_data).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=self.queue_name
        )

    async def process_messages(self, callback: Callable):
        while True:
            try:
                await self.connect()
                queue = await self.channel.declare_queue(self.queue_name, durable=True)
                
                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process():
                            try:
                                data = json.loads(message.body.decode())
                                await callback(data)
                            except Exception as e:
                                logger.error(f"Error processing message: {e}")
            except Exception as e:
                logger.error(f"Connection error in process_messages: {e}")
                await asyncio.sleep(self.retry_delay)