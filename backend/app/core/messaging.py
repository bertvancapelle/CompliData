"""RabbitMQ messaging.

Publisher voor tenant-scoped vhosts. At-least-once delivery met
persistente berichten.
"""
import json
import uuid
from datetime import datetime, timezone

import aio_pika

from app.core.config import settings


async def get_connection(tenant_slug: str):
    """Connect to the tenant-specific vhost."""
    vhost = f"cd-{tenant_slug}"
    url = settings.rabbitmq_url.rstrip("/") + f"/{vhost}"
    return await aio_pika.connect_robust(url)


async def publish(
    tenant_slug: str,
    exchange_name: str,
    routing_key: str,
    payload: dict,
):
    """Publish a persistent message to a tenant vhost exchange."""
    payload.setdefault("bericht_id", str(uuid.uuid4()))
    payload.setdefault("verzonden_op", datetime.now(timezone.utc).isoformat())

    connection = await get_connection(tenant_slug)
    async with connection:
        channel = await connection.channel()
        exchange = await channel.get_exchange(exchange_name)
        await exchange.publish(
            aio_pika.Message(
                body=json.dumps(payload).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                content_type="application/json",
                message_id=payload["bericht_id"],
            ),
            routing_key=routing_key,
        )
