from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.cases import EvidenceBundle, EvidenceSource
from app.contracts.cases import EvidenceItem as EvidenceItemContract
from app.db.models import Case, EvidenceItem


class EvidenceCaseNotFoundError(LookupError):
    """Raised when evidence targets a case outside the merchant scope."""


async def list_evidence(
    session: AsyncSession,
    merchant_id: UUID,
    case_id: UUID,
) -> EvidenceBundle:
    """List evidence only for a case owned by the authenticated merchant."""
    case_exists = await session.scalar(
        select(Case.id).where(Case.id == case_id, Case.merchant_id == merchant_id)
    )
    if case_exists is None:
        raise EvidenceCaseNotFoundError("Case was not found for this merchant")

    result = await session.scalars(
        select(EvidenceItem)
        .where(EvidenceItem.case_id == case_id)
        .order_by(EvidenceItem.occurred_at)
    )
    return EvidenceBundle(
        case_id=case_id,
        items=[EvidenceItemContract.model_validate(item) for item in result],
    )


async def add_evidence(
    session: AsyncSession,
    merchant_id: UUID,
    case_id: UUID,
    *,
    source: EvidenceSource,
    kind: str,
    summary: str,
    payload: dict[str, object],
    confidence: float | None = None,
) -> EvidenceItemContract:
    """Attach one evidence item to a merchant-owned case."""
    case_exists = await session.scalar(
        select(Case.id).where(Case.id == case_id, Case.merchant_id == merchant_id)
    )
    if case_exists is None:
        raise EvidenceCaseNotFoundError("Case was not found for this merchant")

    item = EvidenceItem(
        id=uuid4(),
        case_id=case_id,
        source=source,
        kind=kind,
        summary=summary,
        payload=payload,
        confidence=confidence,
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return EvidenceItemContract.model_validate(item)
