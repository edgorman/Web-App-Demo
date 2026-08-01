"""Shared dependencies for FastAPI resources."""
from fastapi import Request
from src.storage.user import UserStorage


def get_user_storage(request: Request) -> UserStorage:
    """Provide the user storage backend the service was constructed with.

    Args:
        request: Incoming request

    Returns:
        The application's user storage backend
    """
    return request.app.state.user_storage
