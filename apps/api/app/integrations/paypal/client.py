from __future__ import annotations

import base64
import json
from collections.abc import Mapping
from typing import TYPE_CHECKING
from uuid import UUID

import httpx

if TYPE_CHECKING:
    from app.integrations.paypal.webhooks import VerifiedPayPalEvent


class PayPalWebhookVerificationError(RuntimeError):
    """Raised when PayPal cannot verify a webhook request."""


class PayPalWebhookClient:
    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        webhook_id: str,
        merchant_id: UUID,
        base_url: str,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._webhook_id = webhook_id
        self._merchant_id = merchant_id
        self._base_url = base_url.rstrip("/")
        self._http = http_client or httpx.AsyncClient(timeout=httpx.Timeout(10.0))
        self._owns_client = http_client is None

    async def close(self) -> None:
        if self._owns_client:
            await self._http.aclose()

    async def verify(
        self,
        headers: Mapping[str, str],
        body: bytes,
    ) -> VerifiedPayPalEvent:
        from app.integrations.paypal.webhooks import VerifiedPayPalEvent

        required_headers = {
            "transmission_id": headers.get("paypal-transmission-id"),
            "transmission_time": headers.get("paypal-transmission-time"),
            "transmission_sig": headers.get("paypal-transmission-sig"),
            "cert_url": headers.get("paypal-cert-url"),
            "auth_algo": headers.get("paypal-auth-algo"),
        }
        if any(value is None for value in required_headers.values()):
            raise PayPalWebhookVerificationError("Missing PayPal transmission headers")

        try:
            webhook_event = json.loads(body)
        except json.JSONDecodeError as exc:
            raise PayPalWebhookVerificationError("Webhook body is not valid JSON") from exc
        if not isinstance(webhook_event, dict):
            raise PayPalWebhookVerificationError("Webhook body must be a JSON object")

        access_token = await self._access_token()
        response = await self._http.post(
            f"{self._base_url}/v1/notifications/verify-webhook-signature",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "webhook_id": self._webhook_id,
                "webhook_event": webhook_event,
                **required_headers,
            },
        )
        if response.status_code >= 400:
            raise PayPalWebhookVerificationError("PayPal rejected webhook verification")
        result = response.json()
        if result.get("verification_status") != "SUCCESS":
            raise PayPalWebhookVerificationError("PayPal webhook signature is invalid")

        event_id = webhook_event.get("id")
        event_type = webhook_event.get("event_type")
        if not isinstance(event_id, str) or not isinstance(event_type, str):
            raise PayPalWebhookVerificationError("Webhook is missing id or event_type")
        return VerifiedPayPalEvent(event_id, event_type, self._merchant_id, webhook_event)

    async def _access_token(self) -> str:
        response = await self._http.post(
            f"{self._base_url}/v1/oauth2/token",
            content="grant_type=client_credentials",
            headers={
                "Accept": "application/json",
                "Accept-Language": "en_US",
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": "Basic "
                + base64.b64encode(f"{self._client_id}:{self._client_secret}".encode()).decode(),
            },
        )
        if response.status_code >= 400:
            raise PayPalWebhookVerificationError("PayPal OAuth failed")
        token = response.json().get("access_token")
        if not isinstance(token, str) or not token:
            raise PayPalWebhookVerificationError("PayPal OAuth response has no access token")
        return token
