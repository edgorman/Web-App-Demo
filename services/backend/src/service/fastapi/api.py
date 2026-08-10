"""FastAPI implementation of the API interface."""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.service.api import APIServiceInterface
from src.service.fastapi.middleware.authenticate import add_authenticate_middleware
from src.service.fastapi.resources.v1.hello import HelloResource
from src.service.fastapi.resources.v1.users import UserResource
from src.config.service import ServiceConfig
from src.storage.user import UserStorage

API_V1_PREFIX = "/api/v1"


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

        # Expose storage to route handlers via `_dependencies.get_user_storage`
        self.app.state.user_storage = user_storage

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

        # Include resources with /api/v1 prefix. Each protected route enforces its own
        # authorization via the `authorize` dependency (see
        # src/service/fastapi/dependencies/authorize.py) rather than a central rule set —
        # it runs after routing, so it needs no ordering against the middleware above beyond
        # authentication having already set `request.user`.
        self.app.include_router(HelloResource(), prefix=API_V1_PREFIX, tags=["hello"])
        self.app.include_router(UserResource(user_storage), prefix=API_V1_PREFIX, tags=["users"])

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
