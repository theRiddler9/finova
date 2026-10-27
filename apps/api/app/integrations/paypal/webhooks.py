from collections.abc import Mapping
from dataclasses import dataclass
from uuid import UUID

import httpx
from fastapi import HTTPException, Request, status

from app.core.config import get_settings
from app.integrations.paypal.client import PayPalWebhookClient


@dataclass(frozen=True)
class VerifiedPayPalEvent:
    event_id: str
    event_type: str
    merchant_id: UUID
    payload: dict[str, object]


class PayPalWebhookVerifier:
    """Integration seam for PayPal's remote signature verification API."""

    async def verify(
        self,
        headers: Mapping[str, str],
        body: bytes,
    ) -> VerifiedPayPalEvent:
        del headers, body
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PayPal webhook verification is not configured",
        )


def get_paypal_webhook_verifier() -> PayPalWebhookVerifier:
    return PayPalWebhookVerifier()


async def verify_paypal_request(request: Request) -> VerifiedPayPalEvent:
    settings = get_settings()
    merchant_id = settings.paypal_merchant_id
    if (
        not settings.paypal_client_id
        or not settings.paypal_client_secret
        or not settings.paypal_webhook_id
        or merchant_id is None
    ):
        verifier = get_paypal_webhook_verifier()
        return await verifier.verify(request.headers, await request.body())

    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as http_client:
        client = PayPalWebhookClient(
            client_id=settings.paypal_client_id,
            client_secret=settings.paypal_client_secret,
            webhook_id=settings.paypal_webhook_id,
            merchant_id=merchant_id,
            base_url=settings.paypal_api_base_url,
            http_client=http_client,
        )
        return await client.verify(request.headers, await request.body())
