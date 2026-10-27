from datetime import UTC, datetime, timedelta
from enum import StrEnum


class DeadlineStatus(StrEnum):
    OPEN = "OPEN"
    DUE_SOON = "DUE_SOON"
    EXPIRED = "EXPIRED"


def evaluate_deadline(deadline: datetime, *, now: datetime | None = None) -> DeadlineStatus:
    """Classify a response deadline without silently dropping expired cases."""
    current = now or datetime.now(UTC)
    if deadline <= current:
        return DeadlineStatus.EXPIRED
    if deadline < current + timedelta(hours=24):
        return DeadlineStatus.DUE_SOON
    return DeadlineStatus.OPEN
