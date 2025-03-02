from config.config import K8sWorkflowSubmitHandlerConfig
from scheduling.workflow import WorkflowSubmitHandler


class K8sWorkflowSubmitHandler(WorkflowSubmitHandler):
    def __init__(self, config: K8sWorkflowSubmitHandlerConfig) -> None:
        """Initialise a K8sWorkflowSubmitHandler class

        Args:
            config: the config needed to initialise the handler
        """
        self.__service_account_key = config.SERVICE_ACCOUNT_KEY  # example

    def submit(self, file_path: str) -> None:
        """Submit a workflow at the given file path.

        Args:
            file_path: the file path to the workflow for submission
        """
        raise NotImplementedError("submit is not implemented")
