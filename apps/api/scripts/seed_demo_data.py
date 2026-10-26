"""Insert deterministic synthetic data for local backend demos."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.contracts.cases import CaseStatus, EvidenceSource
from app.db.base import session_factory
from app.db.models import Case, EvidenceItem, Merchant, WebhookEvent, WebhookEventStatus

DEMO_MERCHANT_ID = UUID("00000000-0000-0000-0000-000000000001")
CASE_DELIVERED_ID = UUID("00000000-0000-0000-0000-000000000101")
CASE_REVIEW_ID = UUID("00000000-0000-0000-0000-000000000102")


async def seed() -> None:
    now = datetime.now(UTC).replace(microsecond=0)
    async with session_factory() as session:
        merchant = await session.get(Merchant, DEMO_MERCHANT_ID)
        if merchant is None:
            session.add(Merchant(id=DEMO_MERCHANT_ID, name="Demo Merchant"))

        cases = [
            Case(
                id=CASE_DELIVERED_ID,
                merchant_id=DEMO_MERCHANT_ID,
                paypal_dispute_id="PP-DISPUTE-DEMO-001",
                status=CaseStatus.READY_FOR_REVIEW,
                response_deadline=now + timedelta(days=3),
            ),
            Case(
                id=CASE_REVIEW_ID,
                merchant_id=DEMO_MERCHANT_ID,
                paypal_dispute_id="PP-DISPUTE-DEMO-002",
                status=CaseStatus.COLLECTING,
                response_deadline=now + timedelta(hours=12),
            ),
        ]
        for case in cases:
            if await session.get(Case, case.id) is None:
                session.add(case)

        evidence = [
            EvidenceItem(
                id=UUID("00000000-0000-0000-0000-000000001001"),
                case_id=CASE_DELIVERED_ID,
                source=EvidenceSource.SHOPIFY,
                kind="order",
                occurred_at=now - timedelta(days=8),
                summary="Synthetic order for a $200 jacket was placed and fulfilled.",
                payload={"order_value": 200, "currency": "USD", "fulfillment_status": "fulfilled"},
            ),
            EvidenceItem(
                id=UUID("00000000-0000-0000-0000-000000001002"),
                case_id=CASE_DELIVERED_ID,
                source=EvidenceSource.SHIPPO,
                kind="delivery_confirmation",
                occurred_at=now - timedelta(days=3),
                summary="Synthetic carrier scan records delivery at the merchant-provided address.",
                payload={"tracking_status": "delivered", "address_match": True},
            ),
            EvidenceItem(
                id=UUID("00000000-0000-0000-0000-000000001003"),
                case_id=CASE_DELIVERED_ID,
                source=EvidenceSource.VISION,
                kind="delivery_photo",
                occurred_at=now - timedelta(days=3),
                summary="Synthetic delivery photo shows a package at the matching address.",
                payload={"address_match": True, "delivered_signal": True},
                confidence=0.94,
            ),
            EvidenceItem(
                id=UUID("00000000-0000-0000-0000-000000001004"),
                case_id=CASE_REVIEW_ID,
                source=EvidenceSource.ZENDESK,
                kind="customer_message",
                occurred_at=now - timedelta(days=1),
                summary="Synthetic ticket contains a customer delivery question awaiting review.",
                payload={"sentiment": "neutral", "requires_review": True},
            ),
        ]
        for item in evidence:
            if await session.get(EvidenceItem, item.id) is None:
                session.add(item)

        events = [
            WebhookEvent(
                id=UUID("00000000-0000-0000-0000-000000002001"),
                merchant_id=DEMO_MERCHANT_ID,
                event_id="DEMO-EVENT-001",
                event_type="CUSTOMER.DISPUTE.CREATED",
                status=WebhookEventStatus.PROCESSED,
                payload={"resource": {"dispute_id": "PP-DISPUTE-DEMO-001"}},
            ),
            WebhookEvent(
                id=UUID("00000000-0000-0000-0000-000000002002"),
                merchant_id=DEMO_MERCHANT_ID,
                event_id="DEMO-EVENT-002",
                event_type="CUSTOMER.DISPUTE.CREATED",
                status=WebhookEventStatus.QUEUED,
                payload={"resource": {"dispute_id": "PP-DISPUTE-DEMO-002"}},
            ),
        ]
        for event in events:
            if await session.get(WebhookEvent, event.id) is None:
                session.add(event)

        await session.commit()
    print("Synthetic demo data is ready for merchant 00000000-0000-0000-0000-000000000001")


if __name__ == "__main__":
    asyncio.run(seed())
