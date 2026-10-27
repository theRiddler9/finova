from collections.abc import Iterator

import pytest

from app.core.config import get_settings


@pytest.fixture
def configured_auth(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Keep authentication behavior deterministic when the repository .env is absent."""
    monkeypatch.setenv("AUTH_JWT_SECRET", "test-auth-secret")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
