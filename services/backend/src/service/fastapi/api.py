"""FastAPI implementation of the API interface."""
import uvicorn
from fastapi import FastAPI
from src.service.api import APIInterface
from src.service.fastapi.resources.v1 import hello
from src.config.service import ServiceConfig


class FastAPIService(APIInterface):
    """FastAPI implementation of the API interface."""

    def __init__(self, config: ServiceConfig):
        """Initialize FastAPI service.

        Args:
            config: Service configuration
        """
        self.config = config
        self.app = FastAPI(
            title=config.app_name,
            version=config.app_version,
        )

        # Include routers
        self.app.include_router(hello.router, tags=["hello"])

    def run(self, host: str = None, port: int = None, reload: bool = None):
        """Run the FastAPI server.

        Args:
            host: Host to bind to (defaults to config value)
            port: Port to bind to (defaults to config value)
            reload: Enable auto-reload (defaults to config value)
        """
        uvicorn.run(
            self.app,
            host=host or self.config.host,
            port=port or self.config.port,
            reload=reload if reload is not None else self.config.reload,
        )
