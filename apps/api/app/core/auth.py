from uuid import UUID

import jwt
from fastapi import Header, HTTPException, status

from app.core.config import get_settings


async def get_current_merchant_id(authorization: str | None = Header(default=None)) -> UUID:
    """Validate a bearer token and return its merchant scope, failing closed."""
    settings = get_settings()
    if not settings.auth_jwt_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is not configured",
        )
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required",
        )

    token = authorization.removeprefix("Bearer ").strip()
    try:
        claims = jwt.decode(token, settings.auth_jwt_secret, algorithms=["HS256"])
        merchant_id = UUID(str(claims["merchant_id"]))
    except (jwt.PyJWTError, KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
        ) from exc
    return merchant_id
