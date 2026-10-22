from datetime import UTC, datetime

import pytest

from app.pipeline.case_creation import InvalidDisputePayload, _deadline


def test_parses_paypal_response_deadline() -> None:
    result = _deadline({"resource": {"response_due_date": "2026-11-01T10:30:00Z"}})
    assert result == datetime(2026, 11, 1, 10, 30, tzinfo=UTC)


def test_rejects_missing_response_deadline() -> None:
    with pytest.raises(InvalidDisputePayload):
        _deadline({"resource": {}})
