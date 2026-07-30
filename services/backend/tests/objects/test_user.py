"""Test user object."""
import pytest
from pydantic import ValidationError
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
