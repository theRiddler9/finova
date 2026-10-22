from httpx import ASGITransport, AsyncClient

from app.main import app


async def test_transition_route_requires_authentication() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v1/cases/00000000-0000-0000-0000-000000000000/transition",
            json={"target": "SUBMITTED", "approved": True},
        )

    assert response.status_code == 503
