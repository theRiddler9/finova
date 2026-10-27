from app.contracts.cases import CaseStatus
from app.domain.approval import approve_for_submission
from app.domain.case_state import transition_case


def test_lifecycle_dependencies_allow_review_to_submission() -> None:
    status = transition_case(CaseStatus.COLLECTING, CaseStatus.READY_FOR_REVIEW)
    assert approve_for_submission(status, approved=True) is CaseStatus.SUBMITTED
