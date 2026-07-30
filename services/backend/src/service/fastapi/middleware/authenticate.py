"""Authentication middleware verifying provider bearer tokens."""
from fastapi import FastAPI
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from starlette.authentication import AuthCredentials, AuthenticationBackend, AuthenticationError
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import HTTPConnection
from starlette.responses import JSONResponse, Response
from src.config.auth import (
    AUTHENTICATED_SCOPE,
    AUTHORIZATION_BEARER_PREFIX,
    AUTHORIZATION_HEADER,
    AUTHORIZATION_PROVIDER_HEADER,
    AuthProvider,
)
from src.objects.user import User


class AuthError(AuthenticationError):
    """Authentication failure carrying the HTTP status code it should produce."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class AuthenticateBackend(AuthenticationBackend):
    """Verifies a bearer token from a supported provider and resolves it to a User."""

    def __init__(self, google_client_id: str):
        self.__google_client_id = google_client_id

    async def authenticate(self, connection: HTTPConnection) -> tuple[AuthCredentials, User] | None:
        if AUTHORIZATION_HEADER not in connection.headers:
            return None

        auth = connection.headers[AUTHORIZATION_HEADER]
        if not auth.startswith(AUTHORIZATION_BEARER_PREFIX):
            raise AuthError(
                400, f"`{AUTHORIZATION_HEADER}` header malformed, must start with `{AUTHORIZATION_BEARER_PREFIX}`."
            )
        token = auth[len(AUTHORIZATION_BEARER_PREFIX):]

        if AUTHORIZATION_PROVIDER_HEADER not in connection.headers:
            raise AuthError(400, f"`{AUTHORIZATION_PROVIDER_HEADER}` is missing.")

        try:
            provider = AuthProvider(connection.headers[AUTHORIZATION_PROVIDER_HEADER])
        except ValueError:
            raise AuthError(
                400,
                f"`{connection.headers[AUTHORIZATION_PROVIDER_HEADER]}` is not a valid value for "
                f"`{AUTHORIZATION_PROVIDER_HEADER}`.",
            )

        match provider:
            case AuthProvider.GOOGLE:
                provider_data = self._auth_google(token)
            case _:
                raise AuthError(501, f"Provider `{provider.value}` has not been implemented.")

        return AuthCredentials([AUTHENTICATED_SCOPE]), self._get_user(provider_data)

    def _auth_google(self, token: str) -> dict:
        if not self.__google_client_id:
            raise AuthError(500, "Google authentication is not configured")

        try:
            return google_id_token.verify_oauth2_token(
                token, google_requests.Request(), audience=self.__google_client_id
            )
        except ValueError as e:
            raise AuthError(401, f"Invalid Google ID token: {e}")

    def _get_user(self, provider_data: dict) -> User:
        return User(
            id=provider_data["sub"],
            email=provider_data["email"],
            name=provider_data.get("name", provider_data["email"]),
        )

    @staticmethod
    def on_error(connection: HTTPConnection, exception: AuthError) -> Response:
        return JSONResponse(status_code=exception.status_code, content={"detail": exception.detail})


def add_authenticate_middleware(app: FastAPI, google_client_id: str):
    """Register the authentication middleware (Google Sign-In, for now).

    Args:
        app: FastAPI application to attach the middleware to
        google_client_id: OAuth 2.0 client ID used to verify Google ID tokens
    """
    backend = AuthenticateBackend(google_client_id=google_client_id)
    app.add_middleware(AuthenticationMiddleware, backend=backend, on_error=backend.on_error)
