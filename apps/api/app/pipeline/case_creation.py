from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.cases import CaseStatus
from app.db.models import Case, WebhookEvent


class InvalidDisputePayload(ValueError):
    """Raised when a webhook does not contain the required dispute fields."""


def _required_string(payload: dict[str, Any], path: tuple[str, ...]) -> str:
    value: Any = payload
    for key in path:
        if not isinstance(value, dict):
            raise InvalidDisputePayload(f"Missing dispute field: {'.'.join(path)}")
        value = value.get(key)
    if not isinstance(value, str) or not value:
        raise InvalidDisputePayload(f"Missing dispute field: {'.'.join(path)}")
    return value


def _deadline(payload: dict[str, Any]) -> datetime:
    raw = _required_string(payload, ("resource", "response_due_date"))
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise InvalidDisputePayload("Invalid resource.response_due_date") from exc


async def ensure_case_for_event(session: AsyncSession, event: WebhookEvent) -> Case:
    """Create or return the case represented by a persisted dispute event."""
    dispute_id = _required_string(event.payload, ("resource", "dispute_id"))
    existing = await session.scalar(
        select(Case).where(
            Case.merchant_id == event.merchant_id,
            Case.paypal_dispute_id == dispute_id,
        )
    )
    if existing is not None:
        return existing

    case = Case(
        merchant_id=event.merchant_id,
        paypal_dispute_id=dispute_id,
        response_deadline=_deadline(event.payload),
        status=CaseStatus.RECEIVED,
    )
    session.add(case)
    await session.flush()
    return case
