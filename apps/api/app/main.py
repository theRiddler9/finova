from fastapi import FastAPI

from app.api.cases import router as cases_router
from app.api.webhooks import router as webhooks_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Merchant-only PayPal dispute defense API.",
)
app.include_router(cases_router)
app.include_router(webhooks_router)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    """Return a lightweight liveness response."""
    return {"status": "ok"}
