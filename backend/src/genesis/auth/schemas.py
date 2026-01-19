"""Authentication schemas."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class UserType(str, Enum):
    """Type of authenticated user."""

    STUDENT = "student"
    GUARDIAN = "guardian"
    ADMIN = "admin"


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_type: UserType


class TokenPayload(BaseModel):
    """JWT token payload."""

    sub: str  # User ID
    user_type: UserType
    exp: datetime
    iat: datetime


class CleverAuthRequest(BaseModel):
    """Clever OAuth callback request."""

    code: str
    state: str | None = None


class CleverUserInfo(BaseModel):
    """User info from Clever SSO."""

    clever_id: str
    email: EmailStr | None = None
    first_name: str
    last_name: str
    school_id: str
    district_id: str
    grade: str | None = None
    birthdate: str | None = None  # ISO format


class IDmeAuthRequest(BaseModel):
    """ID.me OAuth callback request."""

    code: str
    state: str | None = None


class IDmeUserInfo(BaseModel):
    """User info from ID.me verification."""

    idme_uuid: str
    email: EmailStr
    first_name: str
    last_name: str
    verified: bool = False
    verification_level: str | None = None


class GuardianRegistration(BaseModel):
    """Guardian registration data."""

    idme_user_id: str
    email: EmailStr
    coppa_consent: bool = Field(..., description="COPPA consent acknowledgment")


class StudentRegistration(BaseModel):
    """Student registration data."""

    clever_id: str
    school_id: str
    birthdate: str  # ISO format - must be > 13 years old
    guardian_approval_code: str | None = None


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str
