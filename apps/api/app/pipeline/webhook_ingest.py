from collections.abc import Awaitable, Callable
from typing import Protocol
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.cases import WebhookEvent
from app.db.models import WebhookEvent as WebhookEventModel
from app.db.models import WebhookEventStatus


class WebhookQueue(Protocol):
    async def enqueue(self, event_id: UUID) -> None:
        """Queue background processing for a persisted webhook event."""


class WebhookIngestService:
    """Persist verified webhook events exactly once before queueing work."""

    def __init__(self, session: AsyncSession, queue: WebhookQueue) -> None:
        self._session = session
        self._queue = queue

    async def accept(self, event: WebhookEvent) -> bool:
        """Accept a new event and queue it, returning false for duplicates."""
        existing = await self._session.scalar(
            select(WebhookEventModel).where(
                WebhookEventModel.merchant_id == event.merchant_id,
                WebhookEventModel.event_id == event.event_id,
            )
        )
        if existing is not None:
            return False

        record = WebhookEventModel(
            merchant_id=event.merchant_id,
            event_id=event.event_id,
            event_type=event.event_type,
            payload=event.payload,
            status=WebhookEventStatus.RECEIVED,
        )
        self._session.add(record)
        try:
            await self._session.commit()
        except IntegrityError:
            await self._session.rollback()
            return False

        await self._queue.enqueue(record.id)
        record.status = WebhookEventStatus.QUEUED
        await self._session.commit()
        return True


QueueFactory = Callable[[AsyncSession], Awaitable[WebhookQueue]]
