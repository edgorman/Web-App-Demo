from repository.git import GitEventType, GitHandler
from scheduling.workflow import WorkflowSubmitHandler
from usecase.__cicd_event import CICDEventUsecase


class PullRequestUsecase(CICDEventUsecase):
    def __init__(
        self,
        git_handler: GitHandler,
        workflow_submit_handler: WorkflowSubmitHandler,
    ) -> None:
        super().__init__(git_handler, workflow_submit_handler)

    def run(self, start_commit: str, end_commit: str) -> None:
        """Run the CICD event usecase for a pull request event.

        Args:
            start_commit: the start commit to get changes from
            end_commit: the end commit to get changes until
        """
        super().run(start_commit, end_commit, GitEventType.PULL_REQUEST)
