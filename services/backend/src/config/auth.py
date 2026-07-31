"""Authentication configuration module."""
from enum import Enum
from pydantic import BaseModel


AUTHENTICATED_SCOPE = "authenticated"
AUTHORIZATION_HEADER = "Authorization"
AUTHORIZATION_BEARER_PREFIX = "Bearer "
AUTHORIZATION_PROVIDER_HEADER = "Authorization-Provider"


class AuthProvider(Enum):
    """Supported authentication providers."""

    GOOGLE = "google"


class GoogleAuthConfig(BaseModel):
    """Google Sign-In configuration."""

    client_id: str = ""


class AuthConfig(BaseModel):
    """Authentication configuration."""

    google: GoogleAuthConfig = GoogleAuthConfig()
