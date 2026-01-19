"""Authentication dependencies."""

from typing import Annotated

from fastapi import Depends, Header

from genesis.auth.schemas import TokenPayload, UserType
from genesis.core.exceptions import authentication_exception, authorization_exception
from genesis.core.security import decode_access_token


async def get_token_payload(
    authorization: Annotated[str | None, Header()] = None,
) -> TokenPayload:
    """Extract and validate JWT token from Authorization header."""
    if not authorization:
        raise authentication_exception("Missing authorization header")

    if not authorization.startswith("Bearer "):
        raise authentication_exception("Invalid authorization header format")

    token = authorization[7:]  # Remove "Bearer " prefix

    try:
        payload_dict = decode_access_token(token)
        return TokenPayload(**payload_dict)
    except Exception as e:
        raise authentication_exception(f"Invalid token: {e}")


async def get_current_user(
    token_payload: Annotated[TokenPayload, Depends(get_token_payload)],
) -> dict[str, str]:
    """Get current authenticated user."""
    return {
        "id": token_payload.sub,
        "user_type": token_payload.user_type.value,
    }


async def get_current_student(
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
) -> dict[str, str]:
    """Ensure current user is a student."""
    if current_user["user_type"] != UserType.STUDENT.value:
        raise authorization_exception("Only students can access this resource")
    return current_user


async def get_current_guardian(
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
) -> dict[str, str]:
    """Ensure current user is a guardian."""
    if current_user["user_type"] != UserType.GUARDIAN.value:
        raise authorization_exception("Only guardians can access this resource")
    return current_user


async def get_current_admin(
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
) -> dict[str, str]:
    """Ensure current user is an admin."""
    if current_user["user_type"] != UserType.ADMIN.value:
        raise authorization_exception("Only admins can access this resource")
    return current_user
