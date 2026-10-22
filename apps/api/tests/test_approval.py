import pytest

from app.contracts.cases import CaseStatus
from app.domain.approval import ApprovalRequiredError, approve_for_submission


def test_approval_allows_review_ready_submission() -> None:
    assert (
        approve_for_submission(CaseStatus.READY_FOR_REVIEW, approved=True)
        is CaseStatus.SUBMITTED
    )


def test_submission_requires_explicit_approval() -> None:
    with pytest.raises(ApprovalRequiredError):
        approve_for_submission(CaseStatus.READY_FOR_REVIEW, approved=False)


def test_submission_cannot_bypass_case_state() -> None:
    with pytest.raises(ApprovalRequiredError):
        approve_for_submission(CaseStatus.COLLECTING, approved=True)
