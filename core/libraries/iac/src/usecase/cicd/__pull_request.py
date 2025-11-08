from repository.git import GitEventType, GitHandler
from scheduling.workflow import WorkflowSubmitHandler

from .__event import CICDEventUsecase


class PullRequestUsecase(CICDEventUsecase):
    def __init__(
        self,
        git_handler: GitHandler,
        workflow_submit_handler: WorkflowSubmitHandler,
    ) -> None:
        super().__init__(git_handler, workflow_submit_handler)

    def run(self, number: int) -> None:
        """Run the CICD event usecase for a pull-request event.

        Args:
            number: the number of the pull-request
        """
        try:
            start_commit, end_commit = self._git_handler.get_pull_request_commits(number)
        except Exception as e:
            raise Exception(f"Could not get the start/end commit from pull-request event: {str(e)}")

        super().run(start_commit, end_commit, GitEventType.PULL_REQUEST)
