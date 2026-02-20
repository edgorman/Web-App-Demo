"""Main entry point for the backend service."""
from src.config.service import ServiceConfig
from src.service.fastapi.api import FastAPIService

# Create service configuration
config = ServiceConfig()

# Create FastAPI service
service = FastAPIService(config)

# Expose the app for uvicorn
app = service.get_app()
