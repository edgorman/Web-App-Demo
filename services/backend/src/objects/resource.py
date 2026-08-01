"""Resource base class defining per-action authorization."""
from abc import ABC
from enum import Enum
from typing import Protocol, runtime_checkable


@runtime_checkable
class AuthorizableUser(Protocol):
    """The caller an authorization check is made on behalf of.

    Structurally matches both `src.objects.user.User` and Starlette's `UnauthenticatedUser`,
    so a resource can be checked without knowing whether the request was authenticated.
    """

    @property
    def is_authenticated(self) -> bool:
        ...


class Resource(ABC):
    """Base class for anything a request can act on, carrying its own authorization rules.

    Implementations declare the actions they support by overriding the nested `Action`
    enum, and the rules for those actions by overriding `is_authorized`.
    """

    class Action(Enum):
        """Actions available on a resource — empty here, overridden by implementations."""

    def is_authorized(self, user: AuthorizableUser, action: "Resource.Action") -> bool:
        """Check whether a user may perform an action on this resource.

        Denies everything by default, so a resource is only ever accessible through rules
        it has explicitly opted into.

        Args:
            user: Caller the request was made by, authenticated or not
            action: Action the caller wants to perform on this resource

        Returns:
            True if the action is authorized, otherwise False
        """
        return False
