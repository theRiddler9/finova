from collections.abc import AsyncIterator
from uuid import UUID

from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

from app.core.config import get_settings


class ArqWebhookQueue:
    """ARQ adapter used by the webhook ingest service."""

    def __init__(self, redis: ArqRedis) -> None:
        self._redis = redis

    async def enqueue(self, event_id: UUID) -> None:
        await self._redis.enqueue_job("process_webhook", str(event_id))


async def get_webhook_queue() -> AsyncIterator[ArqWebhookQueue]:
    settings = get_settings()
    redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    try:
        yield ArqWebhookQueue(redis)
    finally:
        await redis.close()
