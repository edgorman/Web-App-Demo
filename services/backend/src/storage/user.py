"""User storage interface definition."""
from abc import ABC, abstractmethod
from typing import Optional
from src.objects.user import User


class UserStorage(ABC):
    """Abstract base class for user persistence backends."""

    @abstractmethod
    def get(self, user_id: str) -> Optional[User]:
        """Fetch a user by id.

        Args:
            user_id: Unique identifier of the user

        Returns:
            The user if found, otherwise None
        """
        ...

    @abstractmethod
    def create(self, user: User) -> User:
        """Persist a new user.

        Args:
            user: User to create

        Returns:
            The created user
        """
        ...

    @abstractmethod
    def update(self, user: User) -> User:
        """Persist changes to an existing user.

        Args:
            user: User with updated fields

        Returns:
            The updated user
        """
        ...

    @abstractmethod
    def delete(self, user_id: str) -> None:
        """Delete a user by id.

        Args:
            user_id: Unique identifier of the user
        """
        ...
