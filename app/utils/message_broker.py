import json
import asyncio
from typing import Dict, Any, Optional, Callable
from aio_pika import connect_robust, Message, Channel, Queue
from aio_pika.abc import AbstractRobustConnection
from app.core.config import settings


class MessageBroker:

    def __init__(self):
        self.connection: Optional[AbstractRobustConnection] = None
        self.channel: Optional[Channel] = None

    async def connect(self) -> None:
        self.connection = await connect_robust(settings.rabbitmq_url)
        self.channel = await self.connection.channel()

    async def close(self) -> None:
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()

    async def publish_message(
        self,
        queue_name: str,
        message: Dict[str, Any],
        priority: int = 0,
    ) -> None:
        if not self.channel:
            await self.connect()

        queue = await self.channel.declare_queue(queue_name, durable=True)

        message_body = json.dumps(message).encode()
        await self.channel.default_exchange.publish(
            Message(
                body=message_body,
                delivery_mode=2,
                priority=priority,
            ),
            routing_key=queue_name,
        )

    async def consume_messages(
        self,
        queue_name: str,
        callback: Callable,
        prefetch_count: int = 1,
    ) -> None:
        if not self.channel:
            await self.connect()

        await self.channel.set_qos(prefetch_count=prefetch_count)
        queue = await self.channel.declare_queue(queue_name, durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        data = json.loads(message.body.decode())
                        await callback(data)
                    except Exception as e:
                        print(f"Error processing message: {e}")


message_broker = MessageBroker()


async def publish_transfer_task(transfer_id: int) -> None:
    await message_broker.publish_message(
        settings.rabbitmq_transfer_queue,
        {"transfer_id": transfer_id, "action": "process"},
    )


async def publish_notification_task(
    user_id: int,
    message: str,
    notification_type: str = "info",
) -> None:
    await message_broker.publish_message(
        settings.rabbitmq_notification_queue,
        {
            "user_id": user_id,
            "message": message,
            "type": notification_type,
        },
    )


async def publish_fx_update_task() -> None:
    await message_broker.publish_message(
        settings.rabbitmq_fx_update_queue,
        {"action": "update_rates"},
    )
