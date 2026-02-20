"""Test message object."""
import pytest
from pydantic import ValidationError
from src.objects.message import Message
from src.objects.response import APIResponse


def test_message_creation():
    """Test creating a message object."""
    message = Message(message="test message")
    assert message.message == "test message"


def test_message_validation():
    """Test message validation."""
    with pytest.raises(ValidationError):
        Message()  # Should fail without message field


def test_api_response_creation():
    """Test creating an API response."""
    message = Message(message="test")
    response = APIResponse(data=message)
    assert response.data == message
    assert response.success is True
    assert response.timestamp is not None


def test_api_response_with_metadata():
    """Test API response with custom metadata."""
    message = Message(message="test")
    response = APIResponse(data=message, success=False, message="Error occurred")
    assert response.data == message
    assert response.success is False
    assert response.message == "Error occurred"
