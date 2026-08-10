"""User object model."""
from pydantic import BaseModel
from src.objects.resource import AuthorizableUser, Resource


class User(Resource, BaseModel):
    """Authenticated user profile, sourced from a verified auth provider token."""

    class Action(Resource.Action):
        """Actions available on a user."""

        GET_BY_ID = "get_by_id"
        UPDATE_FIELD = "update_field"
        DELETE = "delete"

    id: str
    email: str
    name: str

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.name

    def is_user_authorized(self, user: AuthorizableUser, action: Resource.Action) -> bool:
        """Check whether a user may perform an action on this user profile.

        Any authenticated user may look up a profile by id, but only the user themselves
        may update their fields or delete their account — other users and unauthenticated
        callers are not authorized.

        Args:
            user: Caller the request was made by, authenticated or not
            action: Action the caller wants to perform on this user

        Returns:
            True if the action is authorized, otherwise False
        """
        if not user.is_authenticated:
            return False

        match action:
            case User.Action.GET_BY_ID:
                return True
            case User.Action.UPDATE_FIELD | User.Action.DELETE:
                return isinstance(user, User) and user.id == self.id
            case _:
                return False
