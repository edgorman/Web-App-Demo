"""Test user object."""
import pytest
from pydantic import ValidationError
from starlette.authentication import UnauthenticatedUser
from src.objects.resource import Resource
from src.objects.user import User


def test_user_creation():
    """Test creating a user object."""
    user = User(id="123", email="user@example.com", name="Test User")
    assert user.id == "123"
    assert user.email == "user@example.com"
    assert user.name == "Test User"


def test_user_is_authenticated():
    """Test that a user is always considered authenticated."""
    user = User(id="123", email="user@example.com", name="Test User")
    assert user.is_authenticated is True


def test_user_display_name():
    """Test that display_name returns the user's name."""
    user = User(id="123", email="user@example.com", name="Test User")
    assert user.display_name == "Test User"


def test_user_validation():
    """Test user validation."""
    with pytest.raises(ValidationError):
        User(id="123")  # Should fail without email and name fields


def test_user_actions():
    """Test that the user resource declares its available actions."""
    assert [action.value for action in User.Action] == ["get_by_id", "update_field", "delete"]
    assert isinstance(User.Action.DELETE, Resource.Action)


@pytest.mark.parametrize("action", list(User.Action))
def test_user_authorizes_itself(action):
    """Test that a user is authorized for every action on their own profile."""
    user = User(id="123", email="user@example.com", name="Test User")
    assert user.is_authorized(user, action) is True


def test_user_authorizes_other_users_to_read_only():
    """Test that another user may read the profile, but not update or delete it."""
    user = User(id="123", email="user@example.com", name="Test User")
    other = User(id="456", email="other@example.com", name="Other User")

    assert user.is_authorized(other, User.Action.GET_BY_ID) is True
    assert user.is_authorized(other, User.Action.UPDATE_FIELD) is False
    assert user.is_authorized(other, User.Action.DELETE) is False


@pytest.mark.parametrize("action", list(User.Action))
def test_user_denies_unauthenticated_callers(action):
    """Test that an unauthenticated caller is denied every action."""
    user = User(id="123", email="user@example.com", name="Test User")
    assert user.is_authorized(UnauthenticatedUser(), action) is False


def test_user_denies_unknown_actions():
    """Test that an action from another resource is denied."""
    class OtherAction(Resource.Action):
        UNKNOWN = "unknown"

    user = User(id="123", email="user@example.com", name="Test User")
    assert user.is_authorized(user, OtherAction.UNKNOWN) is False
