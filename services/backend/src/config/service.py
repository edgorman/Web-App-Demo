"""Service configuration module using pydantic settings."""
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class FastAPIServiceConfig(BaseModel):
    """FastAPI-specific configuration."""

    host: str = "0.0.0.0"
    port: int = 8080
    reload: bool = False
    app_name: str = "Web-App-Demo Backend"
    app_version: str = "0.1.0"
    # CORS configuration - empty list by default, must be explicitly configured
    # Set via SERVICE__FASTAPI__CORS_ALLOW_ORIGINS environment variable
    cors_allow_origins: list[str] = []
    cors_allow_credentials: bool = False
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]


class ServiceConfig(BaseSettings):
    """Service configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="SERVICE__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
    )

    fastapi: FastAPIServiceConfig = FastAPIServiceConfig()
