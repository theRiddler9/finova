import pytest

from app.contracts.cases import CaseStatus
from app.domain.case_state import InvalidCaseTransition, transition_case


def test_valid_case_transition() -> None:
    assert transition_case(CaseStatus.RECEIVED, CaseStatus.COLLECTING) is CaseStatus.COLLECTING


def test_terminal_case_cannot_transition() -> None:
    with pytest.raises(InvalidCaseTransition):
        transition_case(CaseStatus.WON, CaseStatus.LOST)


def test_review_requires_submission_path() -> None:
    with pytest.raises(InvalidCaseTransition):
        transition_case(CaseStatus.COLLECTING, CaseStatus.SUBMITTED)
