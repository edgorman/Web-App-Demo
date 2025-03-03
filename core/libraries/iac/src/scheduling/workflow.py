from abc import ABC, abstractmethod


class WorkflowSubmitHandler(ABC):
    @abstractmethod
    def submit(self, file_path: str) -> None:
        """Submit a workflow at the given file path."""
