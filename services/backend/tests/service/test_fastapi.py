"""Test FastAPI service."""
from src.service.fastapi.api import FastAPIService


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
