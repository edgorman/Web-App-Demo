"""User object model."""
from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    """Authenticated user profile, sourced from a verified Google ID token."""

    id: str
    email: str
    name: str
    picture: Optional[str] = None
