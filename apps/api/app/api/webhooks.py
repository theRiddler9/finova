from fastapi import APIRouter, Depends

from app.integrations.paypal.webhooks import VerifiedPayPalEvent, verify_paypal_request

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/paypal", status_code=202)
async def receive_paypal_webhook(
    event: VerifiedPayPalEvent = Depends(verify_paypal_request),
) -> dict[str, object]:
    """Acknowledge only events that passed PayPal verification."""
    return {"accepted": True, "event_id": event.event_id}
