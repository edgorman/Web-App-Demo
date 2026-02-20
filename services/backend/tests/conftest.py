"""Shared pytest fixtures."""
import pytest
from fastapi.testclient import TestClient
from src.config.service import ServiceConfig
from src.service.fastapi.api import FastAPIService


@pytest.fixture
def service_config():
    """Create a test service configuration."""
    return ServiceConfig()


@pytest.fixture
def fastapi_service(service_config):
    """Create a FastAPI service instance."""
    return FastAPIService(service_config)


@pytest.fixture
def test_client(fastapi_service):
    """Create a test client for the FastAPI service."""
    return TestClient(fastapi_service.app)
