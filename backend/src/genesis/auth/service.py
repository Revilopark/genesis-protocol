"""Authentication service."""

import logging
from datetime import timedelta
from urllib.parse import urlencode

import httpx

from genesis.auth.schemas import TokenResponse, UserType
from genesis.config import settings
from genesis.core.exceptions import AuthenticationError
from genesis.core.security import create_access_token, create_refresh_token, decode_access_token

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for Clever SSO and ID.me."""

    CLEVER_AUTHORIZE_URL = "https://clever.com/oauth/authorize"
    CLEVER_TOKEN_URL = "https://clever.com/oauth/tokens"
    CLEVER_API_URL = "https://api.clever.com"

    IDME_AUTHORIZE_URL = "https://api.id.me/oauth/authorize"
    IDME_TOKEN_URL = "https://api.id.me/oauth/token"
    IDME_API_URL = "https://api.id.me"

    def get_clever_login_url(self, redirect_uri: str | None = None) -> str:
        """Generate Clever OAuth authorization URL."""
        params = {
            "response_type": "code",
            "client_id": settings.clever_client_id,
            "redirect_uri": redirect_uri or settings.clever_redirect_uri,
            "scope": "read:students read:user_id",
        }
        return f"{self.CLEVER_AUTHORIZE_URL}?{urlencode(params)}"

    def get_idme_login_url(self, redirect_uri: str | None = None) -> str:
        """Generate ID.me OAuth authorization URL."""
        params = {
            "response_type": "code",
            "client_id": settings.idme_client_id,
            "redirect_uri": redirect_uri or settings.idme_redirect_uri,
            "scope": "openid email profile",
        }
        return f"{self.IDME_AUTHORIZE_URL}?{urlencode(params)}"

    async def handle_clever_callback(self, code: str) -> TokenResponse:
        """Exchange Clever authorization code for tokens."""
        async with httpx.AsyncClient() as client:
            # Exchange code for Clever access token
            token_response = await client.post(
                self.CLEVER_TOKEN_URL,
                data={
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.clever_redirect_uri,
                },
                auth=(settings.clever_client_id, settings.clever_client_secret),
            )

            if token_response.status_code != 200:
                raise AuthenticationError("Failed to exchange Clever authorization code")

            clever_tokens = token_response.json()
            clever_access_token = clever_tokens["access_token"]

            # Fetch user info from Clever
            user_response = await client.get(
                f"{self.CLEVER_API_URL}/v3.0/me",
                headers={"Authorization": f"Bearer {clever_access_token}"},
            )

            if user_response.status_code != 200:
                raise AuthenticationError("Failed to fetch Clever user info")

            user_data = user_response.json()["data"]

            # Create internal JWT tokens
            user_id = f"clever_{user_data['id']}"
            access_token = create_access_token(
                data={"sub": user_id, "user_type": UserType.STUDENT.value},
                expires_delta=timedelta(minutes=settings.jwt_access_token_expire_minutes),
            )
            refresh_token = create_refresh_token(
                data={"sub": user_id, "user_type": UserType.STUDENT.value},
            )

            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.jwt_access_token_expire_minutes * 60,
                user_type=UserType.STUDENT,
            )

    async def handle_idme_callback(self, code: str) -> TokenResponse:
        """Exchange ID.me authorization code for tokens."""
        async with httpx.AsyncClient() as client:
            # Exchange code for ID.me access token
            token_response = await client.post(
                self.IDME_TOKEN_URL,
                data={
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.idme_redirect_uri,
                    "client_id": settings.idme_client_id,
                    "client_secret": settings.idme_client_secret,
                },
            )

            if token_response.status_code != 200:
                raise AuthenticationError("Failed to exchange ID.me authorization code")

            idme_tokens = token_response.json()
            idme_access_token = idme_tokens["access_token"]

            # Fetch user info from ID.me
            user_response = await client.get(
                f"{self.IDME_API_URL}/api/public/v3/attributes.json",
                headers={"Authorization": f"Bearer {idme_access_token}"},
            )

            if user_response.status_code != 200:
                raise AuthenticationError("Failed to fetch ID.me user info")

            user_data = user_response.json()

            # Create internal JWT tokens
            user_id = f"idme_{user_data.get('uuid', user_data.get('id'))}"
            access_token = create_access_token(
                data={"sub": user_id, "user_type": UserType.GUARDIAN.value},
                expires_delta=timedelta(minutes=settings.jwt_access_token_expire_minutes),
            )
            refresh_token = create_refresh_token(
                data={"sub": user_id, "user_type": UserType.GUARDIAN.value},
            )

            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.jwt_access_token_expire_minutes * 60,
                user_type=UserType.GUARDIAN,
            )

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token."""
        try:
            payload = decode_access_token(refresh_token)

            if payload.get("type") != "refresh":
                raise AuthenticationError("Invalid refresh token")

            user_id = payload["sub"]
            user_type = UserType(payload["user_type"])

            access_token = create_access_token(
                data={"sub": user_id, "user_type": user_type.value},
                expires_delta=timedelta(minutes=settings.jwt_access_token_expire_minutes),
            )
            new_refresh_token = create_refresh_token(
                data={"sub": user_id, "user_type": user_type.value},
            )

            return TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
                expires_in=settings.jwt_access_token_expire_minutes * 60,
                user_type=user_type,
            )
        except Exception as e:
            raise AuthenticationError(f"Failed to refresh token: {e}") from e

    async def logout(self, user_id: str, access_token: str | None = None) -> None:
        """Logout user by blacklisting their tokens.

        Args:
            user_id: The user's ID
            access_token: Optional access token to blacklist
        """
        try:
            from genesis.core.redis import get_redis, _redis_available

            if not _redis_available:
                logger.warning("Redis unavailable, logout without token blacklisting")
                return

            redis_client = get_redis()

            # Blacklist the current access token if provided
            if access_token:
                try:
                    payload = decode_access_token(access_token)
                    # Get token expiration time
                    exp = payload.get("exp", 0)
                    # Calculate TTL (time until token expires)
                    import time
                    ttl = max(0, int(exp - time.time()))

                    if ttl > 0:
                        # Add token to blacklist with TTL matching expiration
                        await redis_client.setex(
                            f"blacklist:token:{access_token[:32]}",  # Use prefix of token as key
                            ttl,
                            "1",
                        )
                        logger.info(f"Access token blacklisted for user {user_id}")
                except Exception as e:
                    logger.warning(f"Failed to decode token for blacklisting: {e}")

            # Increment user's token version to invalidate all existing refresh tokens
            await redis_client.incr(f"user:token_version:{user_id}")

            # Clear any cached user data
            await redis_client.delete(f"user:session:{user_id}")

            logger.info(f"User {user_id} logged out successfully")

        except Exception as e:
            logger.error(f"Error during logout for user {user_id}: {e}")
            # Don't raise - logout should be best-effort

    async def is_token_blacklisted(self, token: str) -> bool:
        """Check if a token is blacklisted.

        Args:
            token: The access token to check

        Returns:
            True if blacklisted, False otherwise
        """
        try:
            from genesis.core.redis import get_redis, _redis_available

            if not _redis_available:
                return False

            redis_client = get_redis()
            result = await redis_client.exists(f"blacklist:token:{token[:32]}")
            return bool(result)

        except Exception as e:
            logger.warning(f"Failed to check token blacklist: {e}")
            return False

    async def get_user_token_version(self, user_id: str) -> int:
        """Get the current token version for a user.

        Used to invalidate all tokens when user logs out everywhere.

        Args:
            user_id: The user's ID

        Returns:
            Current token version (0 if not set)
        """
        try:
            from genesis.core.redis import get_redis, _redis_available

            if not _redis_available:
                return 0

            redis_client = get_redis()
            version = await redis_client.get(f"user:token_version:{user_id}")
            return int(version) if version else 0

        except Exception as e:
            logger.warning(f"Failed to get token version: {e}")
            return 0
