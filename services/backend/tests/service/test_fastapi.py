"""Test FastAPI service."""
from src.service.fastapi.api import FastAPIService


def test_fastapi_service_initialization(service_config):
    """Test FastAPI service initialization."""
    service = FastAPIService(service_config)
    assert service.config == service_config
    assert service.app is not None


def test_fastapi_service_get_app(fastapi_service):
    """Test getting the FastAPI app."""
    app = fastapi_service.get_app()
    assert app is not None
    assert app.title == "Web-App-Demo Backend"
    assert app.version == "0.1.0"


def test_hello_endpoint(test_client):
    """Test the hello endpoint."""
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from the Web-App-Demo backend!"}
