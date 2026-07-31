"""Shared pytest fixtures."""
import pytest
from fastapi.testclient import TestClient
from src.config.auth import AuthConfig, GoogleAuthConfig
from src.config.service import ServiceConfig, FastAPIServiceConfig, CORSConfig
from src.service.fastapi.api import FastAPIService
from tests.fakes import InMemoryUserStorage


@pytest.fixture
def service_config():
    """Create a test service configuration."""
    return ServiceConfig(
        fastapi=FastAPIServiceConfig(
            cors=CORSConfig(
                allow_origins=["https://example.com"]
            )
        ),
        auth=AuthConfig(
            google=GoogleAuthConfig(client_id="test-client-id.apps.googleusercontent.com")
        )
    )


@pytest.fixture
def user_storage():
    """Create an in-memory user storage instance for tests."""
    return InMemoryUserStorage()


@pytest.fixture
def fastapi_service(service_config, user_storage):
    """Create a FastAPI service instance."""
    return FastAPIService(service_config, user_storage)


@pytest.fixture
def test_client(fastapi_service):
    """Create a test client for the FastAPI service."""
    return TestClient(fastapi_service.app)
