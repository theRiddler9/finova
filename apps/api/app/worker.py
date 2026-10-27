from typing import cast
from uuid import UUID

import structlog
from arq import create_pool
from arq.connections import ArqRedis, RedisSettings
from sqlalchemy import select

from app.core.config import get_settings
from app.db.base import session_factory
from app.db.models import WebhookEvent, WebhookEventStatus
from app.pipeline.case_creation import ensure_case_for_event

logger = structlog.get_logger(__name__)
settings = get_settings()


async def process_webhook(ctx: dict[str, object], event_id: str) -> None:
    """Process one persisted webhook event in the background worker."""
    del ctx
    parsed_event_id = UUID(event_id)
    async with session_factory() as session:
        event = await session.scalar(select(WebhookEvent).where(WebhookEvent.id == parsed_event_id))
        if event is None:
            logger.warning("webhook_event_missing", event_id=event_id)
            return
        if event.status is WebhookEventStatus.PROCESSED:
            return

        # Integration-specific evidence collection is intentionally delegated to
        # the pipeline after signature verification and event deduplication.
        logger.info(
            "webhook_event_processing",
            event_id=event.event_id,
            event_type=event.event_type,
        )
        await ensure_case_for_event(session, event)
        event.status = WebhookEventStatus.PROCESSED
        await session.commit()


async def startup(ctx: dict[str, object]) -> None:
    """Initialize worker resources."""
    ctx["redis"] = await create_pool(RedisSettings.from_dsn(settings.redis_url))


async def shutdown(ctx: dict[str, object]) -> None:
    """Close worker resources."""
    redis = ctx.pop("redis", None)
    if redis is not None:
        await cast(ArqRedis, redis).close()


class WorkerSettings:
    functions = [process_webhook]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
