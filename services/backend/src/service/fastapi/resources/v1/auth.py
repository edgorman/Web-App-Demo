"""Google Sign-In authentication resource."""
from fastapi import APIRouter, HTTPException
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from pydantic import BaseModel
from src.objects.user import User
from src.service.fastapi.resources.v1._objects import Request, Response


class GoogleLoginRequest(BaseModel):
    """Request payload carrying the Google Identity Services credential."""

    credential: str


def build_router(client_id: str) -> APIRouter:
    """Build the Google auth router.

    Args:
        client_id: The OAuth 2.0 client ID that issued ID tokens must be
            audienced for. See https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid

    Returns:
        APIRouter: Router exposing the /auth/google endpoint.
    """
    router = APIRouter()

    @router.post("/auth/google", response_model=Response[User])
    def login_with_google(request: Request[GoogleLoginRequest]):
        """Verify a Google ID token and return the authenticated user.

        Args:
            request: Wrapped GoogleLoginRequest containing the ID token
                credential returned by the Google Identity Services library.

        Returns:
            Response[User]: The verified user's profile.
        """
        if not client_id:
            raise HTTPException(
                status_code=500,
                detail="Google authentication is not configured",
            )

        try:
            id_info = google_id_token.verify_oauth2_token(
                request.data.credential,
                google_requests.Request(),
                audience=client_id,
            )
        except ValueError:
            raise HTTPException(status_code=401, detail="Invalid Google ID token")

        return Response(
            data=User(
                id=id_info["sub"],
                email=id_info["email"],
                name=id_info.get("name", id_info["email"]),
                picture=id_info.get("picture"),
            )
        )

    return router
