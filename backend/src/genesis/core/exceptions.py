"""Custom exception classes."""

from fastapi import HTTPException, status


class GenesisException(Exception):
    """Base exception for Genesis Protocol."""

    def __init__(self, message: str = "An error occurred"):
        self.message = message
        super().__init__(self.message)


class NotFoundError(GenesisException):
    """Resource not found error."""

    pass


class ValidationError(GenesisException):
    """Validation error."""

    pass


class AuthenticationError(GenesisException):
    """Authentication error."""

    pass


class AuthorizationError(GenesisException):
    """Authorization error."""

    pass


class RateLimitError(GenesisException):
    """Rate limit exceeded error."""

    pass


class ContentGenerationError(GenesisException):
    """Content generation pipeline error."""

    pass


class ModerationError(GenesisException):
    """Content moderation error."""

    pass


# HTTP Exception factory functions
def not_found_exception(detail: str = "Resource not found") -> HTTPException:
    """Create a 404 Not Found exception."""
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def validation_exception(detail: str = "Validation error") -> HTTPException:
    """Create a 422 Validation Error exception."""
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


def authentication_exception(detail: str = "Could not validate credentials") -> HTTPException:
    """Create a 401 Unauthorized exception."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def authorization_exception(detail: str = "Not authorized to perform this action") -> HTTPException:
    """Create a 403 Forbidden exception."""
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def rate_limit_exception(detail: str = "Rate limit exceeded") -> HTTPException:
    """Create a 429 Too Many Requests exception."""
    return HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)
