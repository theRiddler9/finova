from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.cases import WebhookEvent
from app.db.base import get_db_session
from app.integrations.paypal.webhooks import VerifiedPayPalEvent, verify_paypal_request
from app.pipeline.queue import ArqWebhookQueue, get_webhook_queue
from app.pipeline.webhook_ingest import WebhookIngestService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/paypal", status_code=202)
async def receive_paypal_webhook(
    event: VerifiedPayPalEvent = Depends(verify_paypal_request),
    session: AsyncSession = Depends(get_db_session),
    queue: ArqWebhookQueue = Depends(get_webhook_queue),
) -> dict[str, object]:
    """Persist and queue only events that passed PayPal verification."""
    accepted = await WebhookIngestService(session, queue).accept(
        WebhookEvent(
            event_id=event.event_id,
            event_type=event.event_type,
            merchant_id=event.merchant_id,
            payload=event.payload,
        )
    )
    return {"accepted": accepted, "event_id": event.event_id}
