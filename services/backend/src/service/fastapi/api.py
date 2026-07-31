"""FastAPI implementation of the API interface."""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.service.api import APIServiceInterface
from src.service.fastapi.middleware.authenticate import add_authenticate_middleware
from src.service.fastapi.resources.v1 import hello
from src.config.service import ServiceConfig
from src.storage.user import UserStorage


class FastAPIService(APIServiceInterface):
    """FastAPI implementation of the API interface."""

    def __init__(self, config: ServiceConfig, user_storage: UserStorage):
        """Initialize FastAPI service.

        Args:
            config: Service configuration
            user_storage: Storage backend used to persist authenticated users
        """
        self.config = config.fastapi
        self.app = FastAPI(
            title=self.config.app_name,
            version=self.config.app_version,
        )

        # Add authentication middleware (Google Sign-In, for now)
        add_authenticate_middleware(self.app, config.auth.google.client_id, user_storage)

        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.cors.allow_origins,
            allow_credentials=self.config.cors.allow_credentials,
            allow_methods=self.config.cors.allow_methods,
            allow_headers=self.config.cors.allow_headers,
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
            host=host or self.config.host,
            port=port or self.config.port,
            reload=reload if reload is not None else self.config.reload,
        )
