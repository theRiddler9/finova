from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.cases import CaseRead, CaseStatus
from app.db.models import Case


async def list_cases(
    session: AsyncSession,
    merchant_id: UUID,
    *,
    status: CaseStatus | None = None,
) -> list[CaseRead]:
    """List cases for one merchant, never across tenants."""
    statement = select(Case).where(Case.merchant_id == merchant_id).order_by(Case.response_deadline)
    if status is not None:
        statement = statement.where(Case.status == status)
    result = await session.scalars(statement)
    return [CaseRead.model_validate(case) for case in result]


async def get_case(
    session: AsyncSession,
    merchant_id: UUID,
    case_id: UUID,
) -> CaseRead | None:
    """Fetch one case only when it belongs to the requested merchant."""
    statement = select(Case).where(Case.id == case_id, Case.merchant_id == merchant_id)
    case = await session.scalar(statement)
    return CaseRead.model_validate(case) if case is not None else None
