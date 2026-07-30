"""FastAPI implementation of the API interface."""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.service.api import APIServiceInterface
from src.service.fastapi.resources.v1 import auth, hello
from src.config.service import FastAPIServiceConfig


class FastAPIService(APIServiceInterface):
    """FastAPI implementation of the API interface."""

    def __init__(self, config: FastAPIServiceConfig, google_client_id: str = ""):
        """Initialize FastAPI service.

        Args:
            config: FastAPI service configuration
            google_client_id: Google OAuth 2.0 client ID used to verify
                Google Sign-In ID tokens
        """
        self.config = config
        self.app = FastAPI(
            title=config.app_name,
            version=config.app_version,
        )

        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=config.cors.allow_origins,
            allow_credentials=config.cors.allow_credentials,
            allow_methods=config.cors.allow_methods,
            allow_headers=config.cors.allow_headers,
        )

        # Include routers with /api/v1 prefix
        self.app.include_router(hello.router, prefix="/api/v1", tags=["hello"])
        self.app.include_router(
            auth.build_router(google_client_id), prefix="/api/v1", tags=["auth"]
        )

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
