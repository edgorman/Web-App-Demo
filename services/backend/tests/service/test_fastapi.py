"""Test FastAPI service."""
from fastapi.testclient import TestClient
from src.config.auth import AuthConfig, GoogleAuthConfig
from src.service.fastapi.api import FastAPIService
from src.service.fastapi.resources.v1 import auth as auth_resource


def test_fastapi_service_initialization(service_config):
    """Test FastAPI service initialization."""
    service = FastAPIService(service_config.fastapi)
    assert service.config == service_config.fastapi
    assert service.app is not None


def test_fastapi_service_app_properties(fastapi_service):
    """Test FastAPI app properties."""
    app = fastapi_service.app
    assert app is not None
    assert app.title == "Web-App-Demo Backend"
    assert app.version == "0.1.0"


def test_hello_endpoint(test_client):
    """Test the hello endpoint."""
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


def test_google_login_success(test_client, monkeypatch):
    """Test that a valid Google credential returns the verified user."""
    def fake_verify_oauth2_token(credential, request, audience):
        assert credential == "fake-credential"
        assert audience == "test-client-id.apps.googleusercontent.com"
        return {
            "sub": "1234567890",
            "email": "user@example.com",
            "name": "Test User",
            "picture": "https://example.com/pic.jpg",
        }

    monkeypatch.setattr(auth_resource.google_id_token, "verify_oauth2_token", fake_verify_oauth2_token)

    response = test_client.post("/api/v1/auth/google", json={"data": {"credential": "fake-credential"}})
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] is True
    assert response_data["data"] == {
        "id": "1234567890",
        "email": "user@example.com",
        "name": "Test User",
        "picture": "https://example.com/pic.jpg",
    }


def test_google_login_invalid_token(test_client, monkeypatch):
    """Test that an invalid Google credential is rejected."""
    def fake_verify_oauth2_token(credential, request, audience):
        raise ValueError("Invalid token")

    monkeypatch.setattr(auth_resource.google_id_token, "verify_oauth2_token", fake_verify_oauth2_token)

    response = test_client.post("/api/v1/auth/google", json={"data": {"credential": "bad-credential"}})
    assert response.status_code == 401


def test_google_login_not_configured(service_config):
    """Test that login fails clearly when no client ID is configured."""
    service_config.auth = AuthConfig(google=GoogleAuthConfig(client_id=""))
    service = FastAPIService(service_config.fastapi, service_config.auth.google.client_id)
    client = TestClient(service.app)

    response = client.post("/api/v1/auth/google", json={"data": {"credential": "fake-credential"}})
    assert response.status_code == 500
