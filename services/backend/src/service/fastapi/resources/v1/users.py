"""User endpoint resource."""
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.objects.user import User
from src.service.fastapi.dependencies.authorize import authorize
from src.service.fastapi.resources.v1._dependencies import get_user_storage
from src.service.fastapi.resources.v1._objects import Request, Response
from src.storage.user import UserStorage

router = APIRouter()

USER_ROUTE = "/users/{user_id}"


class UserFields(BaseModel):
    """Fields of a user profile that can be updated, each optional for partial updates."""

    email: Optional[str] = None
    name: Optional[str] = None


def resolve_user(user_id: str, user_storage: UserStorage = Depends(get_user_storage)) -> Optional[User]:
    """Load the user a request targets, for the `authorize` dependency to check and reuse.

    Args:
        user_id: Unique identifier of the user, taken from the route's path parameter
        user_storage: Storage backend used to persist users

    Returns:
        The stored user, or None if no such user exists
    """
    return user_storage.get(user_id)


@router.get(USER_ROUTE, response_model=Response[User])
def get_by_id(user: User = Depends(authorize(User.Action.GET_BY_ID, resolve_user))):
    """Fetch a user profile by id.

    Args:
        user: User resolved by `resolve_user` and authorized by the `authorize` dependency

    Returns:
        Response[User]: The requested user wrapped in API response
    """
    return Response(data=user)


@router.patch(USER_ROUTE, response_model=Response[User])
def update_field(
    request: Request[UserFields],
    user: User = Depends(authorize(User.Action.UPDATE_FIELD, resolve_user)),
    user_storage: UserStorage = Depends(get_user_storage),
):
    """Update one or more fields on a user profile.

    Args:
        request: Fields to update — omitted fields are left unchanged
        user: User resolved by `resolve_user` and authorized by the `authorize` dependency
        user_storage: Storage backend used to persist users

    Returns:
        Response[User]: The updated user wrapped in API response
    """
    updated = user.model_copy(update=request.data.model_dump(exclude_none=True))
    return Response(data=user_storage.update(updated))


@router.delete(USER_ROUTE, response_model=Response[None])
def delete(
    user: User = Depends(authorize(User.Action.DELETE, resolve_user)),
    user_storage: UserStorage = Depends(get_user_storage),
):
    """Delete a user profile.

    Args:
        user: User resolved by `resolve_user` and authorized by the `authorize` dependency
        user_storage: Storage backend used to persist users

    Returns:
        Response[None]: Empty payload wrapped in API response
    """
    user_storage.delete(user.id)
    return Response(data=None, message="User deleted.")
