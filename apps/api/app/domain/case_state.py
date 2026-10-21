from collections.abc import Mapping

from app.contracts.cases import CaseStatus


class InvalidCaseTransition(ValueError):
    """Raised when a case attempts an invalid lifecycle transition."""


VALID_TRANSITIONS: Mapping[CaseStatus, frozenset[CaseStatus]] = {
    CaseStatus.RECEIVED: frozenset({CaseStatus.COLLECTING, CaseStatus.FAILED, CaseStatus.EXPIRED}),
    CaseStatus.COLLECTING: frozenset(
        {CaseStatus.READY_FOR_REVIEW, CaseStatus.FAILED, CaseStatus.EXPIRED}
    ),
    CaseStatus.READY_FOR_REVIEW: frozenset({CaseStatus.SUBMITTED, CaseStatus.EXPIRED}),
    CaseStatus.SUBMITTED: frozenset({CaseStatus.WON, CaseStatus.LOST}),
    CaseStatus.WON: frozenset(),
    CaseStatus.LOST: frozenset(),
    CaseStatus.FAILED: frozenset(),
    CaseStatus.EXPIRED: frozenset(),
}


def can_transition(current: CaseStatus, target: CaseStatus) -> bool:
    """Return whether the target is a valid next lifecycle state."""
    return target in VALID_TRANSITIONS[current]


def transition_case(current: CaseStatus, target: CaseStatus) -> CaseStatus:
    """Validate and return a new case state."""
    if not can_transition(current, target):
        raise InvalidCaseTransition(f"Cannot transition case from {current} to {target}")
    return target
