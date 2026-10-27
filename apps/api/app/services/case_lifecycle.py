from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.cases import CaseRead, CaseStatus
from app.db.models import Case
from app.domain.approval import approve_for_submission
from app.domain.case_state import transition_case


class CaseNotFoundError(LookupError):
    """Raised when a case is absent or belongs to another merchant."""


async def transition_case_status(
    session: AsyncSession,
    merchant_id: UUID,
    case_id: UUID,
    target: CaseStatus,
    *,
    approved: bool = False,
) -> CaseRead:
    """Transition one merchant's case under a row lock."""
    case = await session.scalar(
        select(Case).where(Case.id == case_id, Case.merchant_id == merchant_id).with_for_update()
    )
    if case is None:
        raise CaseNotFoundError("Case was not found for this merchant")

    if target is CaseStatus.SUBMITTED:
        case.status = approve_for_submission(case.status, approved)
    else:
        case.status = transition_case(case.status, target)
    await session.commit()
    await session.refresh(case)
    return CaseRead.model_validate(case)
