from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.cases import CaseRead, CaseStatus, EvidenceBundle
from app.core.auth import get_current_merchant_id
from app.db.base import get_db_session
from app.services.cases import get_case, list_cases
from app.services.evidence import EvidenceCaseNotFoundError, list_evidence

router = APIRouter(prefix="/v1/cases", tags=["cases"])


@router.get("", response_model=list[CaseRead])
async def read_cases(
    status_filter: CaseStatus | None = Query(default=None, alias="status"),
    merchant_id: UUID = Depends(get_current_merchant_id),
    session: AsyncSession = Depends(get_db_session),
) -> list[CaseRead]:
    return await list_cases(session, merchant_id, status=status_filter)


@router.get("/{case_id}", response_model=CaseRead)
async def read_case(
    case_id: UUID,
    merchant_id: UUID = Depends(get_current_merchant_id),
    session: AsyncSession = Depends(get_db_session),
) -> CaseRead:
    case = await get_case(session, merchant_id, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case


@router.get("/{case_id}/evidence", response_model=EvidenceBundle)
async def read_case_evidence(
    case_id: UUID,
    merchant_id: UUID = Depends(get_current_merchant_id),
    session: AsyncSession = Depends(get_db_session),
) -> EvidenceBundle:
    try:
        return await list_evidence(session, merchant_id, case_id)
    except EvidenceCaseNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found") from exc
