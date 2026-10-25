from uuid import uuid4

import httpx
import pytest

from app.integrations.paypal.client import PayPalWebhookClient, PayPalWebhookVerificationError


@pytest.mark.asyncio
async def test_paypal_client_verifies_successful_webhook() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        if request.url.path.endswith("/oauth2/token"):
            return httpx.Response(200, json={"access_token": "sandbox-token"})
        return httpx.Response(200, json={"verification_status": "SUCCESS"})

    client = PayPalWebhookClient(
        client_id="client",
        client_secret="secret",
        webhook_id="webhook",
        merchant_id=uuid4(),
        base_url="https://paypal.test",
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )
    try:
        event = await client.verify(
            {
                "paypal-transmission-id": "transmission",
                "paypal-transmission-time": "2026-10-25T10:00:00Z",
                "paypal-transmission-sig": "signature",
                "paypal-cert-url": "https://paypal.test/cert",
                "paypal-auth-algo": "SHA256withRSA",
            },
            b'{"id":"evt-1","event_type":"CUSTOMER.DISPUTE.CREATED"}',
        )
    finally:
        await client._http.aclose()

    assert event.event_id == "evt-1"
    assert calls == ["/v1/oauth2/token", "/v1/notifications/verify-webhook-signature"]


@pytest.mark.asyncio
async def test_paypal_client_rejects_missing_transmission_headers() -> None:
    client = PayPalWebhookClient(
        client_id="client",
        client_secret="secret",
        webhook_id="webhook",
        merchant_id=uuid4(),
        base_url="https://paypal.test",
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(lambda _: httpx.Response(200))),
    )
    with pytest.raises(PayPalWebhookVerificationError):
        await client.verify({}, b"{}")
    await client._http.aclose()
