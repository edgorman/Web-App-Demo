"""User endpoint resource."""
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from src.objects.user import User
from src.service.fastapi.dependencies.authorize import authorize
from src.service.fastapi.resources.v1._objects import Request, Response
from src.storage.user import UserStorage


class GetUserResponse(BaseModel):
    """Response schema for `GET /users/{user_id}`."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    name: str


class UpdateUserRequest(BaseModel):
    """Request schema for `PATCH /users/{user_id}` — omitted fields are left unchanged."""

    email: Optional[str] = None
    name: Optional[str] = None


class UpdateUserResponse(BaseModel):
    """Response schema for `PATCH /users/{user_id}`."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    name: str


class DeleteUserResponse(BaseModel):
    """Response schema for `DELETE /users/{user_id}`."""

    model_config = ConfigDict(from_attributes=True)

    id: str


class UserResource(APIRouter):
    """API resource for user profiles, mounted at `/users`.

    Routes are built and registered here in `__init__` rather than as class-body methods, so
    `resolve_user` — used as a `Depends(...)` default on each of them — can close over
    `user_storage` directly instead of reaching for it through app-level state. A class-body
    method's default parameter values are evaluated once, when the class itself is defined,
    before any `UserResource` (and therefore its storage handler) exists.
    """

    def __init__(self, user_storage: UserStorage):
        """Initialize the resource and register its routes.

        Args:
            user_storage: Storage backend used to persist users
        """
        super().__init__(prefix="/users")

        def resolve_user(user_id: str) -> Optional[User]:
            """Load the user a request targets, for `authorize` to check and reuse.

            Args:
                user_id: Unique identifier of the user, taken from the route's path parameter

            Returns:
                The stored user, or None if no such user exists
            """
            return user_storage.get(user_id)

        def get_by_id(
            user: User = Depends(authorize(User.Action.GET_BY_ID, resolve_user)),
        ) -> Response[GetUserResponse]:
            """Fetch a user profile by id.

            Args:
                user: User resolved by `resolve_user` and authorized by the `authorize` dependency

            Returns:
                Response[GetUserResponse]: The requested user wrapped in API response
            """
            return Response(data=GetUserResponse.model_validate(user))

        def update_field(
            request: Request[UpdateUserRequest],
            user: User = Depends(authorize(User.Action.UPDATE_FIELD, resolve_user)),
        ) -> Response[UpdateUserResponse]:
            """Update one or more fields on a user profile.

            Args:
                request: Fields to update — omitted fields are left unchanged
                user: User resolved by `resolve_user` and authorized by the `authorize` dependency

            Returns:
                Response[UpdateUserResponse]: The updated user wrapped in API response
            """
            updated = user.model_copy(update=request.data.model_dump(exclude_none=True))
            return Response(data=UpdateUserResponse.model_validate(user_storage.update(updated)))

        def delete(
            user: User = Depends(authorize(User.Action.DELETE, resolve_user)),
        ) -> Response[DeleteUserResponse]:
            """Delete a user profile.

            Args:
                user: User resolved by `resolve_user` and authorized by the `authorize` dependency

            Returns:
                Response[DeleteUserResponse]: The id of the deleted user wrapped in API response
            """
            data = DeleteUserResponse.model_validate(user)
            user_storage.delete(user.id)
            return Response(data=data)

        self.resolve_user = resolve_user
        self.get_by_id = get_by_id
        self.update_field = update_field
        self.delete = delete

        self.add_api_route("/{user_id}", self.get_by_id, methods=["GET"], response_model=Response[GetUserResponse])
        self.add_api_route(
            "/{user_id}", self.update_field, methods=["PATCH"], response_model=Response[UpdateUserResponse]
        )
        self.add_api_route(
            "/{user_id}", self.delete, methods=["DELETE"], response_model=Response[DeleteUserResponse]
        )
