"""Test the `authorize` dependency factory in isolation from FastAPI's DI machinery.

`authorize(action, resolver)` returns a plain function, so it can be called directly with
an explicit `resource` — bypassing the `Depends(resolver)` default — to exercise its
authorization logic without spinning up a request through the app.
"""
from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException
from starlette.authentication import UnauthenticatedUser
from src.objects.user import User
from src.service.fastapi.dependencies.authorize import authorize

OWNER = User(id="owner-id", email="owner@example.com", name="Owner")
OTHER = User(id="other-id", email="other@example.com", name="Other")


def _request(user):
    request = MagicMock()
    request.user = user
    return request


def test_authorize_returns_the_resource_when_authorized():
    """Test that an authorized caller receives the resolved resource back."""
    dependency = authorize(User.Action.GET_BY_ID, resolver=lambda: None)
    assert dependency(request=_request(OWNER), resource=OWNER) is OWNER


def test_authorize_raises_404_when_the_resource_does_not_exist():
    """Test that a resolver returning None is reported as not found, for any caller."""
    dependency = authorize(User.Action.GET_BY_ID, resolver=lambda: None)

    with pytest.raises(HTTPException) as exc_info:
        dependency(request=_request(UnauthenticatedUser()), resource=None)
    assert exc_info.value.status_code == 404


def test_authorize_raises_404_for_an_unauthenticated_denied_caller():
    """Test that a denied unauthenticated caller can't distinguish this from a 404."""
    dependency = authorize(User.Action.DELETE, resolver=lambda: None)

    with pytest.raises(HTTPException) as exc_info:
        dependency(request=_request(UnauthenticatedUser()), resource=OWNER)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Not found."


def test_authorize_raises_403_for_an_authenticated_denied_caller():
    """Test that a denied but already-identified caller gets a forbidden response."""
    dependency = authorize(User.Action.DELETE, resolver=lambda: None)

    with pytest.raises(HTTPException) as exc_info:
        dependency(request=_request(OTHER), resource=OWNER)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Not authorized to perform `delete` on this resource."
