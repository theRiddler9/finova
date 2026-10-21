from fastapi import FastAPI

app = FastAPI(
    title="Finova API",
    version="0.1.0",
    description="Merchant-only PayPal dispute defense API.",
)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    """Return a lightweight liveness response."""
    return {"status": "ok"}
