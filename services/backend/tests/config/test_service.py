"""Test configuration module."""
from src.config.service import ServiceConfig


def test_service_config_defaults():
    """Test default configuration values."""
    config = ServiceConfig()
    assert config.host == "0.0.0.0"
    assert config.port == 8080
    assert config.reload is False
    assert config.app_name == "Web-App-Demo Backend"
    assert config.app_version == "0.1.0"
