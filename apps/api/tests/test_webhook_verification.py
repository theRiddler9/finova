from httpx import ASGITransport, AsyncClient

from app.main import app


async def test_paypal_webhook_fails_closed_without_verifier() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/webhooks/paypal", json={"id": "event"})

    assert response.status_code == 503
