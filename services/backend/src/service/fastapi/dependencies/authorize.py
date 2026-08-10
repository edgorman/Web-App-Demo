"""FastAPI dependency enforcing authorization against a resolved resource."""
from typing import Callable, Optional
from fastapi import Depends, HTTPException, Request, status
from src.objects.resource import Resource


def authorize(action: Resource.Action, resolver: Callable[..., Optional[Resource]]) -> Callable[..., Resource]:
    """Build a dependency that authorizes the caller for an action on a resolved resource.

    `resolver` is wired in as a nested dependency rather than called directly, so it can
    declare whatever path parameters and dependencies it needs (e.g. a storage backend) the
    same way any other FastAPI dependency would — FastAPI resolves it after routing, with
    path parameters already parsed. Routes depend on the callable this returns instead of
    resolving the resource themselves, so they receive the resource already authorized rather
    than reading it a second time.

    Args:
        action: Action the request performs on the resolved resource
        resolver: Dependency that loads the resource a request targets, returning None when
            no such resource exists

    Returns:
        A dependency that raises `HTTPException` when the caller isn't authorized, otherwise
        returns the resolved resource
    """
    def dependency(request: Request, resource: Optional[Resource] = Depends(resolver)) -> Resource:
        if resource is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")

        if not resource.is_user_authorized(request.user, action):
            if not request.user.is_authenticated:
                # An unauthenticated caller can't tell a resource that exists but denies them
                # apart from one that doesn't exist at all.
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not authorized to perform `{action.value}` on this resource.",
            )

        return resource

    return dependency
