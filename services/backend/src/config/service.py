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
