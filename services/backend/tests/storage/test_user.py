"""Test the user storage interface."""
import pytest
from src.storage.user import UserStorage


def test_user_storage_cannot_be_instantiated_directly():
    """UserStorage is abstract and requires a concrete implementation."""
    with pytest.raises(TypeError):
        UserStorage()
