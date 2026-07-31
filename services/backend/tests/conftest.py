"""Shared pytest fixtures."""
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient
from src.config.auth import AuthConfig, GoogleAuthConfig
from src.config.service import ServiceConfig, FastAPIServiceConfig, CORSConfig
from src.service.fastapi.api import FastAPIService
from src.storage.user import UserStorage


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
    """Create a mock user storage for tests.

    `get` defaults to returning None (no stored user yet); `create`/`update` default to
    returning whatever user they were called with, so callers get a realistic value back
    without needing to configure it in every test.
    """
    storage = MagicMock(spec=UserStorage)
    storage.get.return_value = None
    storage.create.side_effect = lambda user: user
    storage.update.side_effect = lambda user: user
    return storage


@pytest.fixture
def fastapi_service(service_config, user_storage):
    """Create a FastAPI service instance."""
    return FastAPIService(service_config, user_storage)


@pytest.fixture
def test_client(fastapi_service):
    """Create a test client for the FastAPI service."""
    return TestClient(fastapi_service.app)
