"""User endpoint resource."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.objects.user import User
from src.service.fastapi.middleware.authorize import AuthorizationRule
from src.service.fastapi.resources.v1._dependencies import get_user_storage
from src.service.fastapi.resources.v1._objects import Request, Response
from src.storage.user import UserStorage

router = APIRouter()

USER_ROUTE = "/users/{user_id}"


class UserFields(BaseModel):
    """Fields of a user profile that can be updated, each optional for partial updates."""

    email: Optional[str] = None
    name: Optional[str] = None


@router.get(USER_ROUTE, response_model=Response[User])
def get_by_id(user_id: str, user_storage: UserStorage = Depends(get_user_storage)):
    """Fetch a user profile by id.

    Args:
        user_id: Unique identifier of the user
        user_storage: Storage backend used to persist users

    Returns:
        Response[User]: The requested user wrapped in API response
    """
    return Response(data=_get_user_or_404(user_storage, user_id))


@router.patch(USER_ROUTE, response_model=Response[User])
def update_field(user_id: str, request: Request[UserFields], user_storage: UserStorage = Depends(get_user_storage)):
    """Update one or more fields on a user profile.

    Args:
        user_id: Unique identifier of the user
        request: Fields to update — omitted fields are left unchanged
        user_storage: Storage backend used to persist users

    Returns:
        Response[User]: The updated user wrapped in API response
    """
    user = _get_user_or_404(user_storage, user_id)
    updated = user.model_copy(update=request.data.model_dump(exclude_none=True))
    return Response(data=user_storage.update(updated))


@router.delete(USER_ROUTE, response_model=Response[None])
def delete(user_id: str, user_storage: UserStorage = Depends(get_user_storage)):
    """Delete a user profile.

    Args:
        user_id: Unique identifier of the user
        user_storage: Storage backend used to persist users

    Returns:
        Response[None]: Empty payload wrapped in API response
    """
    _get_user_or_404(user_storage, user_id)
    user_storage.delete(user_id)
    return Response(data=None, message="User deleted.")


def authorization_rules(user_storage: UserStorage, prefix: str = "") -> list[AuthorizationRule]:
    """Build the authorization rules covering this resource's routes.

    Args:
        user_storage: Storage backend used to load the user a request targets
        prefix: Path prefix the router is mounted under (e.g. `/api/v1`)

    Returns:
        One rule per route, mapping its method onto the user action it performs
    """
    def resolve_user(path_params: dict[str, str]) -> Optional[User]:
        return user_storage.get(path_params["user_id"])

    return [
        AuthorizationRule(
            method=method,
            path=prefix + USER_ROUTE,
            action=action,
            resolver=resolve_user,
        )
        for method, action in (
            ("GET", User.Action.GET_BY_ID),
            ("PATCH", User.Action.UPDATE_FIELD),
            ("DELETE", User.Action.DELETE),
        )
    ]


def _get_user_or_404(user_storage: UserStorage, user_id: str) -> User:
    """Load a user, raising a not-found error when they do not exist.

    Args:
        user_storage: Storage backend used to persist users
        user_id: Unique identifier of the user

    Returns:
        The stored user

    Raises:
        HTTPException: 404 when no user exists with that id
    """
    user = user_storage.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User `{user_id}` not found.")
    return user
