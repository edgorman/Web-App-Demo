"""Test user object."""
import pytest
from pydantic import ValidationError
from src.objects.user import User


def test_user_creation():
    """Test creating a user object."""
    user = User(id="123", email="user@example.com", name="Test User", picture="https://example.com/pic.jpg")
    assert user.id == "123"
    assert user.email == "user@example.com"
    assert user.name == "Test User"
    assert user.picture == "https://example.com/pic.jpg"


def test_user_creation_without_picture():
    """Test creating a user object without a picture."""
    user = User(id="123", email="user@example.com", name="Test User")
    assert user.picture is None


def test_user_validation():
    """Test user validation."""
    with pytest.raises(ValidationError):
        User(id="123")  # Should fail without email and name fields
