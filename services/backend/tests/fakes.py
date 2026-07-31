"""Test doubles shared across test modules."""
from typing import Optional
from src.objects.user import User
from src.storage.user import UserStorage


class InMemoryUserStorage(UserStorage):
    """In-memory `UserStorage` implementation used in place of Firestore in tests."""

    def __init__(self):
        self.users: dict[str, User] = {}

    def get(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)

    def create(self, user: User) -> User:
        self.users[user.id] = user
        return user

    def update(self, user: User) -> User:
        self.users[user.id] = user
        return user

    def delete(self, user_id: str) -> None:
        self.users.pop(user_id, None)
