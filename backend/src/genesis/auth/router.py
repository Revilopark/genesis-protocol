"""Authentication API routes."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from genesis.auth.dependencies import get_current_user
from genesis.auth.schemas import (
    CleverAuthRequest,
    IDmeAuthRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserType,
)
from genesis.auth.service import AuthService
from genesis.config import settings

router = APIRouter()


def get_auth_service() -> AuthService:
    """Dependency for auth service."""
    return AuthService()


@router.get("/clever/login")
async def clever_login_redirect(
    redirect_uri: Annotated[str | None, Query()] = None,
) -> dict[str, str]:
    """Get Clever OAuth login URL."""
    service = AuthService()
    login_url = service.get_clever_login_url(redirect_uri)
    return {"login_url": login_url}


@router.post("/clever/callback", response_model=TokenResponse)
async def clever_callback(
    request: CleverAuthRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """Handle Clever OAuth callback."""
    return await service.handle_clever_callback(request.code)


@router.get("/idme/login")
async def idme_login_redirect(
    redirect_uri: Annotated[str | None, Query()] = None,
) -> dict[str, str]:
    """Get ID.me OAuth login URL."""
    service = AuthService()
    login_url = service.get_idme_login_url(redirect_uri)
    return {"login_url": login_url}


@router.post("/idme/callback", response_model=TokenResponse)
async def idme_callback(
    request: IDmeAuthRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """Handle ID.me OAuth callback."""
    return await service.handle_idme_callback(request.code)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """Refresh access token using refresh token."""
    return await service.refresh_access_token(request.refresh_token)


@router.post("/logout")
async def logout(
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> dict[str, str]:
    """Logout current user (invalidate tokens)."""
    await service.logout(current_user["id"])
    return {"message": "Successfully logged out"}


@router.get("/me")
async def get_current_user_info(
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
) -> dict[str, str]:
    """Get current authenticated user info."""
    return current_user
