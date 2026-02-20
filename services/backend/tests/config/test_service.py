"""Test configuration module."""
from src.config.service import ServiceConfig


def test_service_config_defaults():
    """Test default configuration values."""
    config = ServiceConfig()
    assert config.fastapi.host == "0.0.0.0"
    assert config.fastapi.port == 8080
    assert config.fastapi.reload is False
    assert config.fastapi.app_name == "Web-App-Demo Backend"
    assert config.fastapi.app_version == "0.1.0"
