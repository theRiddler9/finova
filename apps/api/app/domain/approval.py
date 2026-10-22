from app.contracts.cases import CaseStatus
from app.domain.case_state import InvalidCaseTransition, transition_case


class ApprovalRequiredError(PermissionError):
    """Raised when PayPal submission is attempted without merchant approval."""


def approve_for_submission(current_status: CaseStatus, approved: bool) -> CaseStatus:
    """Move a review-ready case to submission only after explicit approval."""
    if not approved:
        raise ApprovalRequiredError("Merchant approval is required before PayPal submission")
    try:
        return transition_case(current_status, CaseStatus.SUBMITTED)
    except InvalidCaseTransition as exc:
        raise ApprovalRequiredError(
            "Only a case in READY_FOR_REVIEW may be submitted to PayPal"
        ) from exc
