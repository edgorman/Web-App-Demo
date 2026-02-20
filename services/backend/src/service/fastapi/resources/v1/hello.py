"""Hello endpoint resource."""
from fastapi import APIRouter
from src.objects.message import Message
from src.objects.response import APIResponse

router = APIRouter()


@router.get("/", response_model=APIResponse[Message])
def read_root():
    """Return a welcome message.

    Returns:
        APIResponse[Message]: Welcome message wrapped in API response
    """
    return APIResponse(
        data=Message(message="Hello from the Web-App-Demo backend!")
    )
