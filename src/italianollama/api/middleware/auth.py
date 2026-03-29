"""Authentication middleware for JWT token validation."""

from datetime import datetime, timedelta, timezone
import logging

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from italianollama.api.config import get_settings
from italianollama.api.exceptions import AuthenticationError

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Create JWT access token.

    Args:
        subject: Token subject (typically student_id)
        expires_delta: Token expiration time. Defaults to JWT_EXPIRATION_HOURS

    Returns:
        Encoded JWT token
    """
    settings = get_settings()

    if expires_delta is None:
        expires_delta = timedelta(hours=settings.jwt_expiration_hours)

    expire = datetime.now(timezone.utc) + expires_delta

    payload = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }

    encoded_jwt = jwt.encode(
        payload,
        settings.auth_secret,
        algorithm=settings.jwt_algorithm,
    )

    return encoded_jwt


def verify_access_token(token: str) -> dict:
    """Verify and decode JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        AuthenticationError: If token is invalid or expired
    """
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.auth_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        raise AuthenticationError("Invalid token")


async def get_current_student(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    """Dependency to extract and verify student_id from token.

    Can be used with @Depends(get_current_student) on route handlers.

    Args:
        request: FastAPI request object
        credentials: HTTP Bearer credentials from Authorization header

    Returns:
        Verified student_id

    Raises:
        AuthenticationError: If credentials missing or invalid
    """
    if not credentials:
        # Also check query parameter as fallback
        student_id = request.query_params.get("student_id")
        if not student_id:
            raise AuthenticationError("Missing authorization credentials")
        return student_id

    token = credentials.credentials
    payload = verify_access_token(token)

    student_id = payload.get("sub")
    if not student_id:
        raise AuthenticationError("Invalid token payload")

    logger.debug(f"Authenticated student: {student_id}")
    return student_id


async def require_api_key(
    request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(security)
) -> str:
    """Dependency for API key validation (alternative to JWT).

    For service-to-service communication.
    """
    if not credentials:
        raise AuthenticationError("Missing API key")

    api_key = credentials.credentials

    # TODO: Implement API key validation against a key store
    # For now, just accept any non-empty key
    if not api_key:
        raise AuthenticationError("Invalid API key")

    return api_key
