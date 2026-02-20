"""Message object model."""
from pydantic import BaseModel


class Message(BaseModel):
    """Message response model."""

    message: str
