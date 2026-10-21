from fastapi import FastAPI

from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Merchant-only PayPal dispute defense API.",
)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    """Return a lightweight liveness response."""
    return {"status": "ok"}
