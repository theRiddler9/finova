from httpx import ASGITransport, AsyncClient

from app.main import app


async def test_case_routes_fail_closed_without_auth_configuration() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/v1/cases")

    assert response.status_code == 503
