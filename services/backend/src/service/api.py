"""API interface definition."""
from abc import ABC, abstractmethod


class API(ABC):
    """Abstract base class for API implementations."""

    @abstractmethod
    def get_app(self):
        """Get the application instance.

        Returns:
            Application instance
        """
        pass

    @abstractmethod
    def run(self, host: str, port: int, reload: bool = False):
        """Run the API server.

        Args:
            host: Host to bind to
            port: Port to bind to
            reload: Enable auto-reload
        """
        pass
