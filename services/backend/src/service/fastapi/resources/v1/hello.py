"""Hello endpoint resource."""
from fastapi import APIRouter
from src.objects.message import Message
from src.service.fastapi.resources.v1._objects import Response

router = APIRouter()


@router.get("/hello", response_model=Response[Message])
def read_root():
    """Return a welcome message.

    Returns:
        Response[Message]: Welcome message wrapped in API response
    """
    return Response(
        data=Message(message="Hello from the Web-App-Demo backend!")
    )
