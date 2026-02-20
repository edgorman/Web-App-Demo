"""Test message object."""
import pytest
from pydantic import ValidationError
from src.objects.message import Message


def test_message_creation():
    """Test creating a message object."""
    message = Message(message="test message")
    assert message.message == "test message"


def test_message_validation():
    """Test message validation."""
    with pytest.raises(ValidationError):
        Message()  # Should fail without message field
