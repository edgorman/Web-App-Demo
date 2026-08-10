"""Hello endpoint resource."""
from fastapi import APIRouter, Request
from src.objects.message import Message
from src.service.fastapi.resources.v1._objects import Response


class HelloResource(APIRouter):
    """API resource for the welcome endpoint, mounted at `/hello`."""

    def __init__(self):
        """Initialize the resource."""
        super().__init__()
        self.add_api_route("/hello", self.get, methods=["GET"], response_model=Response[Message])

    def get(self, request: Request) -> Response[Message]:
        """Return a welcome message, personalized when the caller is authenticated.

        Args:
            request: Incoming request, used to check whether the caller is authenticated

        Returns:
            Response[Message]: Welcome message wrapped in API response
        """
        message = "Hello from the Web-App-Demo backend!"
        if request.user.is_authenticated:
            message = f"Hello {request.user.display_name} from the Web-App-Demo backend!"

        return Response(data=Message(message=message))
