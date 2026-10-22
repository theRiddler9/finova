from collections.abc import Mapping
from dataclasses import dataclass
from uuid import UUID

from fastapi import HTTPException, Request, status


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
    verifier = get_paypal_webhook_verifier()
    return await verifier.verify(request.headers, await request.body())
