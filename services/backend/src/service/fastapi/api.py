"""FastAPI implementation of the API interface."""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.service.api import APIServiceInterface
from src.service.fastapi.resources.v1 import hello
from src.config.service import ServiceConfig


class FastAPIService(APIServiceInterface):
    """FastAPI implementation of the API interface."""

    def __init__(self, config: ServiceConfig):
        """Initialize FastAPI service.

        Args:
            config: Service configuration
        """
        self.config = config
        self.app = FastAPI(
            title=config.fastapi.app_name,
            version=config.fastapi.app_version,
        )

        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=config.fastapi.cors_allow_origins,
            allow_credentials=config.fastapi.cors_allow_credentials,
            allow_methods=config.fastapi.cors_allow_methods,
            allow_headers=config.fastapi.cors_allow_headers,
        )

        # Include routers with /api/v1 prefix
        self.app.include_router(hello.router, prefix="/api/v1", tags=["hello"])

    def run(self, host: str = None, port: int = None, reload: bool = None):
        """Run the FastAPI server.

        Args:
            host: Host to bind to (defaults to config value)
            port: Port to bind to (defaults to config value)
            reload: Enable auto-reload (defaults to config value)
        """
        uvicorn.run(
            self.app,
            host=host or self.config.fastapi.host,
            port=port or self.config.fastapi.port,
            reload=reload if reload is not None else self.config.fastapi.reload,
        )
