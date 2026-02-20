"""Hello endpoint resource."""
from fastapi import APIRouter
from src.objects.message import Message

router = APIRouter()


@router.get("/", response_model=Message)
def read_root():
    """Return a welcome message.

    Returns:
        Message: Welcome message
    """
    return Message(message="Hello from the Web-App-Demo backend!")
