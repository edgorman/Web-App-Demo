"""Test FastAPI service."""
from fastapi.testclient import TestClient
from src.config.auth import AuthConfig, GoogleAuthConfig
from src.objects.user import User
from src.service.fastapi.api import FastAPIService
from src.service.fastapi.middleware import authenticate as authenticate_middleware


def test_fastapi_service_initialization(service_config, user_storage):
    """Test FastAPI service initialization."""
    service = FastAPIService(service_config, user_storage)
    assert service.config == service_config.fastapi
    assert service.app is not None


def test_fastapi_service_app_properties(fastapi_service):
    """Test FastAPI app properties."""
    app = fastapi_service.app
    assert app is not None
    assert app.title == "Web-App-Demo Backend"
    assert app.version == "0.1.0"


def test_hello_endpoint(test_client):
    """Test the hello endpoint for an unauthenticated caller."""
    response = test_client.get("/api/v1/hello")
    assert response.status_code == 200
    response_data = response.json()
    assert "data" in response_data
    assert response_data["data"]["message"] == "Hello from the Web-App-Demo backend!"
    assert "timestamp" in response_data
    assert "success" in response_data
    assert response_data["success"] is True


def test_cors_headers(test_client):
    """Test that CORS middleware is configured."""
    # Make a regular GET request with Origin header
    response = test_client.get("/api/v1/hello", headers={"Origin": "https://example.com"})
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "https://example.com"


def test_hello_endpoint_authenticated(test_client, monkeypatch):
    """Test that a valid Google bearer token personalizes the response."""
    def fake_verify_oauth2_token(credential, request, audience):
        assert credential == "fake-credential"
        assert audience == "test-client-id.apps.googleusercontent.com"
        return {"sub": "1234567890", "email": "user@example.com", "name": "Test User"}

    monkeypatch.setattr(authenticate_middleware.google_id_token, "verify_oauth2_token", fake_verify_oauth2_token)

    response = test_client.get(
        "/api/v1/hello",
        headers={"Authorization": "Bearer fake-credential", "Authorization-Provider": "google"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["message"] == "Hello Test User from the Web-App-Demo backend!"


def test_hello_endpoint_authenticated_creates_user_on_first_login(test_client, user_storage, monkeypatch):
    """Test that a first-time login (no stored user) creates the resolved profile."""
    def fake_verify_oauth2_token(credential, request, audience):
        return {"sub": "1234567890", "email": "user@example.com", "name": "Test User"}

    monkeypatch.setattr(authenticate_middleware.google_id_token, "verify_oauth2_token", fake_verify_oauth2_token)

    test_client.get(
        "/api/v1/hello",
        headers={"Authorization": "Bearer fake-credential", "Authorization-Provider": "google"},
    )

    user_storage.get.assert_called_once_with("1234567890")
    created_user = user_storage.create.call_args.args[0]
    assert created_user == User(id="1234567890", email="user@example.com", name="Test User")
    user_storage.update.assert_not_called()


def test_hello_endpoint_authenticated_updates_user_on_repeat_login(test_client, user_storage, monkeypatch):
    """Test that a returning user (already in storage) is refreshed via update, not create."""
    user_storage.get.return_value = User(id="1234567890", email="user@example.com", name="Old Name")

    def fake_verify_oauth2_token(credential, request, audience):
        return {"sub": "1234567890", "email": "user@example.com", "name": "Updated Name"}

    monkeypatch.setattr(authenticate_middleware.google_id_token, "verify_oauth2_token", fake_verify_oauth2_token)

    response = test_client.get(
        "/api/v1/hello",
        headers={"Authorization": "Bearer fake-credential", "Authorization-Provider": "google"},
    )

    updated_user = user_storage.update.call_args.args[0]
    assert updated_user == User(id="1234567890", email="user@example.com", name="Updated Name")
    user_storage.create.assert_not_called()
    assert response.json()["data"]["message"] == "Hello Updated Name from the Web-App-Demo backend!"


def test_hello_endpoint_invalid_token(test_client, monkeypatch):
    """Test that an invalid Google bearer token is rejected."""
    def fake_verify_oauth2_token(credential, request, audience):
        raise ValueError("Invalid token")

    monkeypatch.setattr(authenticate_middleware.google_id_token, "verify_oauth2_token", fake_verify_oauth2_token)

    response = test_client.get(
        "/api/v1/hello",
        headers={"Authorization": "Bearer bad-credential", "Authorization-Provider": "google"},
    )
    assert response.status_code == 401


def test_hello_endpoint_malformed_authorization_header(test_client):
    """Test that a bearer-less Authorization header is rejected."""
    response = test_client.get(
        "/api/v1/hello",
        headers={"Authorization": "fake-credential", "Authorization-Provider": "google"},
    )
    assert response.status_code == 400


def test_hello_endpoint_missing_provider_header(test_client):
    """Test that a missing Authorization-Provider header is rejected."""
    response = test_client.get("/api/v1/hello", headers={"Authorization": "Bearer fake-credential"})
    assert response.status_code == 400


def test_hello_endpoint_unsupported_provider(test_client):
    """Test that an unsupported Authorization-Provider value is rejected."""
    response = test_client.get(
        "/api/v1/hello",
        headers={"Authorization": "Bearer fake-credential", "Authorization-Provider": "facebook"},
    )
    assert response.status_code == 400


def test_hello_endpoint_not_configured(service_config, user_storage):
    """Test that authentication fails clearly when no client ID is configured."""
    service_config.auth = AuthConfig(google=GoogleAuthConfig(client_id=""))
    service = FastAPIService(service_config, user_storage)
    client = TestClient(service.app)

    response = client.get(
        "/api/v1/hello",
        headers={"Authorization": "Bearer fake-credential", "Authorization-Provider": "google"},
    )
    assert response.status_code == 500
