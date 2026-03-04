"""Shared pytest fixtures."""
import pytest
from fastapi.testclient import TestClient
from src.config.service import ServiceConfig, FastAPIServiceConfig, CORSConfig
from src.service.fastapi.api import FastAPIService


@pytest.fixture
def service_config():
    """Create a test service configuration."""
    return ServiceConfig(
        fastapi=FastAPIServiceConfig(
            cors=CORSConfig(
                allow_origins=["https://example.com"]
            )
        )
    )


@pytest.fixture
def fastapi_service(service_config):
    """Create a FastAPI service instance."""
    return FastAPIService(service_config.fastapi)


@pytest.fixture
def test_client(fastapi_service):
    """Create a test client for the FastAPI service."""
    return TestClient(fastapi_service.app)
