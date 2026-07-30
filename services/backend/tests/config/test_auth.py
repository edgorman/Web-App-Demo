"""Test authentication configuration module."""
from src.config.auth import AuthConfig, GoogleAuthConfig


def test_google_auth_config_defaults():
    """Test default Google auth configuration values."""
    config = GoogleAuthConfig()
    assert config.client_id == ""


def test_auth_config_defaults():
    """Test default auth configuration values."""
    config = AuthConfig()
    assert config.google.client_id == ""


def test_auth_config_custom_client_id():
    """Test auth configuration with a custom client ID."""
    config = AuthConfig(google=GoogleAuthConfig(client_id="my-client-id"))
    assert config.google.client_id == "my-client-id"
