"""API interface definition."""
from abc import ABC, abstractmethod


class APIServiceInterface(ABC):
    """Abstract base class for API implementations."""

    @abstractmethod
    def run(self, host: str, port: int, reload: bool = False):
        """Run the API server.

        Args:
            host: Host to bind to
            port: Port to bind to
            reload: Enable auto-reload
        """
        ...
