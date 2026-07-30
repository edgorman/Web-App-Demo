"""Authentication configuration module."""
from pydantic import BaseModel


class GoogleAuthConfig(BaseModel):
    """Google Sign-In configuration."""

    client_id: str = ""


class AuthConfig(BaseModel):
    """Authentication configuration."""

    google: GoogleAuthConfig = GoogleAuthConfig()
