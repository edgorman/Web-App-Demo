"""User object model."""
from pydantic import BaseModel


class User(BaseModel):
    """Authenticated user profile, sourced from a verified auth provider token."""

    id: str
    email: str
    name: str

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.name
