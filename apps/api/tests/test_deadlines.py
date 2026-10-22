from datetime import UTC, datetime, timedelta

from app.domain.deadlines import DeadlineStatus, evaluate_deadline


def test_expired_deadline_is_explicit() -> None:
    now = datetime.now(UTC)
    assert evaluate_deadline(now - timedelta(minutes=1), now=now) is DeadlineStatus.EXPIRED


def test_future_deadline_remains_open() -> None:
    now = datetime.now(UTC)
    assert evaluate_deadline(now + timedelta(days=1), now=now) is DeadlineStatus.OPEN


def test_deadline_within_24_hours_is_due_soon() -> None:
    now = datetime.now(UTC)
    assert evaluate_deadline(now + timedelta(hours=12), now=now) is DeadlineStatus.DUE_SOON
